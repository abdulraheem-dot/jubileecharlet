import type { AxiosError } from 'axios'

/**
 * Shape of error bodies returned by the backend's custom exception handler,
 * which normalises everything to { message, errors } (or DRF's { detail }).
 */
interface ApiErrorBody {
  message?: string
  detail?: string
  errors?: Record<string, unknown> | unknown[]
}

/**
 * Pull the most useful human-readable message out of a backend error response.
 *
 * The backend returns validation errors as:
 *   { "message": "...", "errors": { <field>: ["...", ...] } }
 * or sometimes as a plain list, or as DRF's { "detail": "..." }.
 * We prefer the specific field error (e.g. "This password is too common.",
 * "User with this email already exists.") over the generic top-level message.
 */
export function extractApiError(
  error: unknown,
  fallback = 'Something went wrong. Please try again.',
): string {
  const data = (error as AxiosError<ApiErrorBody> | undefined)?.response?.data
  if (!data) return fallback

  // DRF permission/not-found style errors
  if (data.detail) return String(data.detail)

  const errors = data.errors
  if (Array.isArray(errors) && errors.length) {
    return String(errors[0])
  }
  if (errors && typeof errors === 'object') {
    for (const value of Object.values(errors)) {
      if (Array.isArray(value) && value.length) return String(value[0])
      if (typeof value === 'string' && value) return value
    }
  }

  if (data.message) return String(data.message)
  return fallback
}
