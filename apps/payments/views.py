import stripe
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from apps.orders.models import Order, Cart
from .tasks import send_order_confirmation_email

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        try:
            order = Order.objects.get(payment_intent_id=intent['id'])
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.payment_method = intent.get('payment_method_types', ['card'])[0]
            order.save()
            # Clear cart
            Cart.objects.filter(user=order.user).delete()
            # Send confirmation email (async via Celery)
            send_order_confirmation_email.delay(order.id)
        except Order.DoesNotExist:
            pass

    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        try:
            order = Order.objects.get(payment_intent_id=intent['id'])
            order.payment_status = 'failed'
            order.status = 'cancelled'
            # Restore stock
            for item in order.items.select_related('product'):
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save(update_fields=['stock'])
            order.save()
        except Order.DoesNotExist:
            pass

    return HttpResponse(status=200)


class PaymentConfigView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return Response({'publishable_key': settings.STRIPE_PUBLISHABLE_KEY})
