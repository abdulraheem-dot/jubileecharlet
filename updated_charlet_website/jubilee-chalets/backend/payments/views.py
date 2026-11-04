import hashlib
import hmac
import json
import logging
import uuid
import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from bookings.models import Booking
from .models import Payment
from .serializers import PaymentSerializer

logger = logging.getLogger('jubilee')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initialize_payment(request):
    """
    Initialise a Paystack payment for a booking.
    The amount is always read from the server — never from the request body.
    """
    booking_id = request.data.get('booking_id')
    if not booking_id:
        return Response({'message': 'booking_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        booking = Booking.objects.get(pk=booking_id, guest=request.user)
    except Booking.DoesNotExist:
        return Response({'message': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

    if booking.payment_status == 'paid':
        return Response({'message': 'This booking has already been paid.'}, status=status.HTTP_400_BAD_REQUEST)

    if booking.status not in ['awaiting_payment', 'pending']:
        return Response({'message': 'This booking cannot be paid at this stage.'}, status=status.HTTP_400_BAD_REQUEST)

    # Amount in kobo (Paystack requires smallest currency unit)
    amount_kobo = int(booking.total_amount * 100)

    # Generate a unique reference
    reference = f"JC-PAY-{uuid.uuid4().hex[:12].upper()}"

    # Detect mock mode: no key, or placeholder key
    is_mock = (not settings.PAYSTACK_SECRET_KEY
               or settings.PAYSTACK_SECRET_KEY.startswith('sk_test_xxx')
               or settings.PAYSTACK_SECRET_KEY.startswith('sk_live_xxx'))

    if is_mock:
        payment = Payment.objects.create(
            booking=booking,
            reference=reference,
            amount=booking.total_amount,
            status=Payment.Status.PENDING,
            metadata={'mock': True},
        )
        logger.warning('Paystack credentials not configured — using mock payment mode')
        return Response({
            'authorization_url': f'{settings.FRONTEND_URL}/payment/result?reference={reference}&mock=true',
            'access_code': 'mock_access_code',
            'reference': reference,
        })

    # Real Paystack initialisation
    payload = {
        'email': request.user.email,
        'amount': amount_kobo,
        'reference': reference,
        'callback_url': f'{settings.FRONTEND_URL}/payment/result',
        'metadata': {
            'booking_id': booking.pk,
            'booking_reference': booking.booking_reference,
            'custom_fields': [
                {'display_name': 'Booking Ref', 'variable_name': 'booking_ref', 'value': booking.booking_reference}
            ],
        },
    }

    try:
        resp = requests.post(
            f'{settings.PAYSTACK_BASE_URL}/transaction/initialize',
            json=payload,
            headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()['data']
    except Exception as exc:
        logger.exception('Paystack initialisation failed: %s', exc)
        return Response({'message': 'Payment service is temporarily unavailable.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    Payment.objects.create(
        booking=booking,
        reference=reference,
        amount=booking.total_amount,
        status=Payment.Status.PENDING,
    )

    return Response({
        'authorization_url': data['authorization_url'],
        'access_code': data['access_code'],
        'reference': reference,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_payment(request, reference):
    """
    Verify a Paystack transaction and update booking status.
    Always verify with Paystack — never trust frontend-supplied status.
    """
    try:
        payment = Payment.objects.get(reference=reference)
    except Payment.DoesNotExist:
        is_mock = (not settings.PAYSTACK_SECRET_KEY
                   or settings.PAYSTACK_SECRET_KEY.startswith('sk_test_xxx')
                   or settings.PAYSTACK_SECRET_KEY.startswith('sk_live_xxx'))
        if is_mock:
            return Response({'status': 'success', 'reference': reference, 'amount': '0', 'channel': 'mock'})
        return Response({'message': 'Payment record not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Ensure this user owns the booking
    if payment.booking.guest != request.user:
        return Response({'message': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if payment.status == Payment.Status.SUCCESS:
        return Response(PaymentSerializer(payment).data)

    is_mock = (not settings.PAYSTACK_SECRET_KEY
               or settings.PAYSTACK_SECRET_KEY.startswith('sk_test_xxx')
               or settings.PAYSTACK_SECRET_KEY.startswith('sk_live_xxx'))

    if is_mock:
        # Mock success for development
        _mark_payment_success(payment)
        return Response(PaymentSerializer(payment).data)

    try:
        resp = requests.get(
            f'{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}',
            headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()['data']
    except Exception as exc:
        logger.exception('Paystack verification failed: %s', exc)
        return Response({'message': 'Verification service unavailable.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if data['status'] == 'success':
        # Validate amount matches what we expect (protect against partial payments)
        expected_kobo = int(payment.amount * 100)
        if data['amount'] < expected_kobo:
            logger.warning('Payment amount mismatch for %s: expected %s, got %s', reference, expected_kobo, data['amount'])
            payment.status = Payment.Status.FAILED
            payment.save()
            return Response({'message': 'Payment amount does not match booking total.'}, status=status.HTTP_400_BAD_REQUEST)

        _mark_payment_success(payment, data)
    else:
        payment.status = Payment.Status.FAILED
        payment.save()

    return Response(PaymentSerializer(payment).data)


def _mark_payment_success(payment, data=None):
    from django.db import transaction as db_transaction
    with db_transaction.atomic():
        payment.status = Payment.Status.SUCCESS
        payment.paid_at = timezone.now()
        if data:
            payment.channel = data.get('channel')
            payment.paystack_id = str(data.get('id', ''))
        payment.save()

        booking = Booking.objects.select_for_update().get(pk=payment.booking_id)
        if booking.payment_status != 'paid':
            booking.payment_status = 'paid'
            booking.status = Booking.Status.CONFIRMED
            booking.confirmed_at = timezone.now()
            booking.save()
            logger.info('Booking confirmed after payment: %s', booking.booking_reference)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def paystack_webhook(request):
    """
    Handle Paystack webhook events.
    Validates signature and processes idempotently.
    """
    signature = request.headers.get('X-Paystack-Signature', '')
    is_mock = (not settings.PAYSTACK_SECRET_KEY
               or settings.PAYSTACK_SECRET_KEY.startswith('sk_test_xxx')
               or settings.PAYSTACK_SECRET_KEY.startswith('sk_live_xxx'))
    if is_mock:
        return Response({'status': 'ok'})

    # Validate HMAC signature
    expected = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        request.body,
        digestmod=hashlib.sha512,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        logger.warning('Invalid webhook signature received')
        return Response({'message': 'Invalid signature.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        event = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({'message': 'Invalid JSON.'}, status=status.HTTP_400_BAD_REQUEST)

    event_type = event.get('event')
    event_data = event.get('data', {})
    reference = event_data.get('reference')

    if event_type == 'charge.success' and reference:
        try:
            payment = Payment.objects.get(reference=reference)
            # Idempotency check
            if event_type not in payment.webhook_events_processed:
                if event_data.get('status') == 'success':
                    _mark_payment_success(payment, event_data)
                payment.webhook_events_processed.append(event_type)
                payment.save()
        except Payment.DoesNotExist:
            logger.warning('Webhook received for unknown reference: %s', reference)

    return Response({'status': 'ok'})
