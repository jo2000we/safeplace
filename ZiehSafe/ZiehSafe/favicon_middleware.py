from django.http import FileResponse
from django.utils.deprecation import MiddlewareMixin


class FaviconMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == '/favicon.ico':
            return FileResponse(open('/var/www/safeplace/static/favicon.ico', 'rb'))
        return None
