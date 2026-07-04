from __future__ import annotations

import json
import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class LoginPageView(TemplateView):
    """Vista de login con soporte GET (HTML) y POST (JSON o form).

    - GET  → renderiza security/login.html
    - POST → autentica y retorna JsonResponse
    """
    template_name = "security/login.html"
    http_method_names = ["get", "post"]

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        try:
            # Detectar content-type: JSON vs formulario tradicional
            if request.content_type == "application/json":
                body = json.loads(request.body)
            else:
                body = request.POST

            username = body.get("username")
            password = body.get("password")

            if not username or not password:
                return JsonResponse(
                    {"resp": False, "error": "Email y contraseña son requeridos"},
                    status=400,
                )

            user = authenticate(request, username=username, password=password)

            if user is None:
                return JsonResponse(
                    {"resp": False, "error": "Credenciales incorrectas"},
                    status=400,
                )

            if not user.is_active:
                logger.warning("Intento de login de usuario inactivo: %s", username)
                return JsonResponse(
                    {"resp": False, "error": "Usuario no habilitado"},
                    status=403,
                )

            login(request, user)
            logger.info("Login exitoso: %s", username)

            return JsonResponse({
                "resp": True,
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "names": f"{user.first_name} {user.last_name}",
                },
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse(
                {"resp": False, "error": "Formato JSON inválido"},
                status=400,
            )
        except Exception:
            logger.exception("Error no controlado en login")
            return JsonResponse(
                {"resp": False, "error": "Error interno del servidor"},
                status=500,
            )


class InicioTemplate(LoginRequiredMixin, TemplateView):
    login_url = "/security/login/"
    redirect_field_name = "redirect_to"
    template_name = "index.html"
