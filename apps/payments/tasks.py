from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_order_confirmation_email(order_id):
    from apps.orders.models import Order
    try:
        order = Order.objects.prefetch_related('items').get(id=order_id)
        items_text = '\n'.join([
            f"  - {item.product_name} x{item.quantity} @ ₹{item.unit_price} = ₹{item.subtotal}"
            for item in order.items.all()
        ])
        message = f"""
Thank you for your order!

Order Number: {order.order_number}
Status: {order.get_status_display()}

Items:
{items_text}

Subtotal:  ₹{order.subtotal}
Shipping:  ₹{order.shipping_cost}
Tax (GST): ₹{order.tax}
Total:     ₹{order.total}

Shipping to:
{order.shipping_name}
{order.shipping_line1}
{order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}
{order.shipping_country}

We'll notify you when your order ships.

Thanks,
The ShopKart Team
        """.strip()

        send_mail(
            subject=f'Order Confirmed — {order.order_number}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email failed for order {order_id}: {e}")
