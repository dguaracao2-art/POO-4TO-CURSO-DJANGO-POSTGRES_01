from __future__ import annotations

import json
import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from .forms import GroupForm, ProfileForm, UserForm
from .models import User
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

class UserListView(PermissionRequiredMixin, ListView):
    permission_required = "security.view_user"
    model = User
    paginate_by = 10
    template_name = "security/user_list.html"
    context_object_name = "user_list"

    def get_queryset(self):
        qs = User.objects.all()

        q = self.request.GET.get("q", "").strip()

        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q)
            )

        return qs.order_by("-date_joined")
    
class UserCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "security.add_user"
    model = User
    form_class = UserForm
    template_name = "security/user_form.html"
    success_url = reverse_lazy("security:user_list")

    def form_valid(self, form):
        messages.success(self.request, "Usuario creado correctamente.")
        return super().form_valid(form)
    
class UserUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "security.change_user"
    model = User
    form_class = UserForm
    template_name = "security/user_form.html"
    success_url = reverse_lazy("security:user_list")
    context_object_name = "user_obj"

    def form_valid(self, form):
        messages.success(self.request, "Usuario actualizado correctamente.")
        return super().form_valid(form)
    
class UserDeactivateView(PermissionRequiredMixin, View):
    permission_required = "security.delete_user"

    def post(self, request, pk):
        user = User.objects.get(pk=pk)

        if user == request.user:
            messages.error(request, "No puedes desactivarte a ti mismo.")
            return redirect("security:user_list")

        user.is_active = False
        user.save()

        messages.success(request, f"Usuario {user.email} desactivado.")
        return redirect("security:user_list")
    
class GroupListView(PermissionRequiredMixin, ListView):
    permission_required = "auth.view_group"
    model = Group
    paginate_by = 10
    template_name = "security/group_list.html"

class GroupCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "auth.add_group"
    model = Group
    form_class = GroupForm
    template_name = "security/group_form.html"
    success_url = reverse_lazy("security:group_list")

    def form_valid(self, form):
        messages.success(self.request, "Rol creado correctamente.")
        return super().form_valid(form)
    
class GroupUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "auth.change_group"
    model = Group
    form_class = GroupForm
    template_name = "security/group_form.html"
    success_url = reverse_lazy("security:group_list")

    def form_valid(self, form):
        messages.success(self.request, "Rol actualizado correctamente.")
        return super().form_valid(form)
    
class ProfileView(LoginRequiredMixin, View):
    template_name = "security/profile.html"

    def get(self, request):
        form = ProfileForm(instance=request.user)
        groups = request.user.groups.all()
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "groups": groups,
            },
        )

    def post(self, request):
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("security:profile")

        groups = request.user.groups.all()

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "groups": groups,
            },
        )