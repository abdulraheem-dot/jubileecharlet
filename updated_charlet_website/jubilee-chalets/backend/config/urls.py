from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path('api/auth/', include('accounts.urls')),
    path('api/rooms/', include('accommodation.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/experiences/', include('experiences.urls')),
    path('api/menu/', include('dining.urls')),
    path('api/events/', include('events.urls')),
    path('api/gallery/', include('gallery.urls')),
    path('api/', include('enquiries.urls')),
    path('api/', include('website.urls')),

    # API schema and docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
