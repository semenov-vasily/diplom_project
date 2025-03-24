# rest_API/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_order_email(order_id, recipient_email):
    """
    Отправляет письмо с подтверждением заказа.
    order_id - ID заказа
    recipient_email - email получателя
    """
    subject = f"Подтверждение заказа #{order_id}"
    message = f"Ваш заказ #{order_id} успешно оформлен!"
    from_email = settings.DEFAULT_FROM_EMAIL  # Убедитесь, что настроен DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [recipient_email])