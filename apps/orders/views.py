from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from decimal import Decimal
import stripe
from django.conf import settings

from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, CheckoutSerializer
from apps.products.models import Product, ProductVariant

stripe.api_key = settings.STRIPE_SECRET_KEY

TAX_RATE = Decimal('0.18')  # 18% GST
FREE_SHIPPING_THRESHOLD = Decimal('999')
SHIPPING_COST = Decimal('99')


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key or request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


class CartView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)


class CartItemAddView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        cart = get_or_create_cart(request)
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id, is_active=True)
        variant = get_object_or_404(ProductVariant, id=variant_id) if variant_id else None

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=variant,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)


class CartItemUpdateView(APIView):
    permission_classes = (permissions.AllowAny,)

    def patch(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        quantity = int(request.data.get('quantity', 1))
        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save()
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)


class CheckoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart = get_or_create_cart(request)
        if not cart.items.exists():
            return Response({'error': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = cart.total
        shipping = Decimal('0') if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST
        tax = (subtotal * TAX_RATE).quantize(Decimal('0.01'))
        total = subtotal + shipping + tax

        # Create Stripe PaymentIntent
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(total * 100),  # paise
                currency='inr',
                metadata={'user_id': request.user.id},
            )
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Create Order
        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            shipping_cost=shipping,
            tax=tax,
            total=total,
            payment_intent_id=intent.id,
            **data
        )

        # Create OrderItems from cart
        for item in cart.items.select_related('product', 'variant'):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                variant_name=f"{item.variant.name}: {item.variant.value}" if item.variant else '',
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            # Decrement stock
            item.product.stock = max(0, item.product.stock - item.quantity)
            item.product.save(update_fields=['stock'])

        return Response({
            'order_id': order.id,
            'order_number': order.order_number,
            'client_secret': intent.client_secret,
            'total': str(total),
        })


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')
