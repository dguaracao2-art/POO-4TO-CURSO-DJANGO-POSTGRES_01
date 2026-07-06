from django import forms
from .models import Factura


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cliente', 'metodo_pago', 'observaciones']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }