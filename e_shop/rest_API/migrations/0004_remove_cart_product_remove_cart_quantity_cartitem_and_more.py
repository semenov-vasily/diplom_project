# Generated by Django 5.1.1 on 2024-09-15 13:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_order_status_order_contact_order_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='product',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='quantity',
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='api.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.product')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(through='api.CartItem', to='api.product'),
        ),
    ]
