# backend/fallback_cors.py
import os
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class FallbackCORSMiddleware(MiddlewareMixin):
    """
    Fallback defensivo para CORS/OPTIONS por si django-cors-headers
    no ejecuta o alguna redirección bloquea el preflight.
    Actívalo con ENABLE_FALLBACK_CORS=true
    """

    def process_request(self, request):
        if os.getenv("ENABLE_FALLBACK_CORS", "false").lower() != "true":
            return None

        if request.method == "OPTIONS":
            resp = HttpResponse("", status=204)
            origin = request.headers.get("Origin", "*")
            # Si usas cookies/credentials, no uses "*": elige el origin real
            resp["Access-Control-Allow-Origin"] = origin
            resp["Vary"] = "Origin"
            resp["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            req_headers = request.headers.get(
                "Access-Control-Request-Headers",
                "content-type,authorization"
            )
            resp["Access-Control-Allow-Headers"] = req_headers
            resp["Access-Control-Max-Age"] = "86400"
            resp["Access-Control-Allow-Credentials"] = "true"
            return resp

        return None

    def process_response(self, request, response):
        if os.getenv("ENABLE_FALLBACK_CORS", "false").lower() != "true":
            return response
        origin = request.headers.get("Origin")
        if origin:
            response["Access-Control-Allow-Origin"] = origin
            response["Vary"] = "Origin"
            response["Access-Control-Allow-Credentials"] = "true"
        return response
