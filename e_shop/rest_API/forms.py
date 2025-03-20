from django import forms
from .models import Product

class ProductAdminForm(forms.ModelForm):
    """
    Кастомная форма для модели Product в административном интерфейсе.
    """
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'size': '40'}),
            # можно добавить дополнительные настройки для других полей
        }

class BulkUpdateForm(forms.Form):
    """
    Форма для массового обновления цены товаров.
    """
    new_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Новая цена"
    )