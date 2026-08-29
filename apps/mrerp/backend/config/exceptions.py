import logging

from rest_framework.views import exception_handler


security_logger = logging.getLogger("mrerp.security")


def _error_code(exc, response):
    codes = getattr(exc, "get_codes", lambda: None)()
    if isinstance(codes, str):
        return codes
    return {
        400: "validation_error",
        401: "not_authenticated",
        403: "permission_denied",
        404: "not_found",
        409: "conflict",
    }.get(response.status_code, "request_failed")


def _detail(data):
    if isinstance(data, dict) and "detail" in data:
        return str(data["detail"])
    if isinstance(data, dict):
        return "Dữ liệu gửi lên không hợp lệ."
    if isinstance(data, list):
        return " ".join(str(item) for item in data)
    return str(data)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    request = context.get("request")
    correlation_id = str(getattr(request, "correlation_id", ""))
    original = response.data
    payload = {
        "code": _error_code(exc, response),
        "detail": _detail(original),
        "correlation_id": correlation_id,
    }
    if isinstance(original, dict) and set(original) != {"detail"}:
        payload["errors"] = original
    response.data = payload

    if response.status_code in {401, 403}:
        user = getattr(request, "user", None)
        security_logger.warning(
            "Protected API request denied",
            extra={
                "correlation_id": correlation_id,
                "actor_id": getattr(user, "pk", None) if getattr(user, "is_authenticated", False) else None,
                "method": getattr(request, "method", ""),
                "path": getattr(request, "path", ""),
                "status_code": response.status_code,
                "error_code": payload["code"],
            },
        )
    return response
