from django.urls import path
from .views import stripe_webhook, PaymentConfigView

urlpatterns = [
    path('config/', PaymentConfigView.as_view(), name='payment-config'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
]
