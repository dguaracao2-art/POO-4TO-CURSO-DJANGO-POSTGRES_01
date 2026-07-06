from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from .forms import ClienteForm
from .models import Cliente


class ClienteListView(PermissionRequiredMixin, ListView):
    permission_required = 'customers.view_cliente'
    model = Cliente
    paginate_by = 10
    template_name = 'customers/cliente_list.html'

    def get_queryset(self):
        qs = Cliente.all_objects.all()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(cedula__icontains=q) | Q(nombre__icontains=q) | Q(email__icontains=q))
        return qs.order_by('nombre')


class ClienteCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'customers.add_cliente'
    model = Cliente
    form_class = ClienteForm
    template_name = 'customers/cliente_form.html'
    success_url = reverse_lazy('customers:cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente registrado correctamente.')
        return super().form_valid(form)


class ClienteUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'customers.change_cliente'
    model = Cliente
    form_class = ClienteForm
    template_name = 'customers/cliente_form.html'
    success_url = reverse_lazy('customers:cliente_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado correctamente.')
        return super().form_valid(form)


class ClienteDeactivateView(PermissionRequiredMixin, View):
    permission_required = 'customers.delete_cliente'

    def post(self, request, pk):
        c = Cliente.all_objects.get(pk=pk)
        c.soft_delete()
        messages.success(request, f'Cliente "{c.nombre}" desactivado.')
        return redirect('customers:cliente_list')