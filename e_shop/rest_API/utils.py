from django.core.mail import send_mail

def send_order_confirmation(order, customer_email):
    subject = f'Order Confirmation - {order.id}'
    message = f'Thank you for your order. Order ID: {order.id}'
    send_mail(subject, message, 'admin@example.com', [customer_email])