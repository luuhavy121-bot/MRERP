import uuid


class CorrelationIdMiddleware:
    """Attach a server-generated correlation identifier to every response."""

    header_name = "X-Correlation-ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.correlation_id = uuid.uuid4()
        response = self.get_response(request)
        response[self.header_name] = str(request.correlation_id)
        return response
