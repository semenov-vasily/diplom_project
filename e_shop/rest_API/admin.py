from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Supplier, Product, Cart, Contact, Order
from .forms import ProductAdminForm, BulkUpdateForm

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Supplier._meta.fields]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = [field.name for field in Product._meta.fields]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-update/', self.admin_site.admin_view(self.bulk_update_view), name='product_bulk_update'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Добавляем ссылку на bulk update в контекст
        extra_context['bulk_update_url'] = 'bulk-update/'
        return super().changelist_view(request, extra_context=extra_context)

    def bulk_update_view(self, request):
        # Реализация bulk update
        if request.method == 'POST':
            form = BulkUpdateForm(request.POST)
            if form.is_valid():
                new_price = form.cleaned_data['new_price']
                updated_count = Product.objects.update(price=new_price)
                self.message_user(request, f"Обновлено товаров: {updated_count}")
                return redirect("..")
        else:
            form = BulkUpdateForm()
        context = dict(
            self.admin_site.each_context(request),
            form=form,
            title="Массовое обновление цен товаров",
        )
        return render(request, "admin/bulk_update.html", context)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Cart._meta.fields]

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Contact._meta.fields]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]