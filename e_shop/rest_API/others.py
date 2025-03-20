from django.core.mail import send_mail

def send_order_mail_confirm(order, customer_email):
    subject = f'Order Confirmation - {order.id}'
    message = f'Thank you for your order. Order ID: {order.id}'
    send_mail(subject, message, 'admin@e-shop.com', [customer_email])