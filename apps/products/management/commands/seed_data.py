from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product
from decimal import Decimal

User = get_user_model()

CATEGORIES = [
    {'name': 'Electronics', 'slug': 'electronics'},
    {'name': 'Clothing', 'slug': 'clothing'},
    {'name': 'Books', 'slug': 'books'},
    {'name': 'Home & Kitchen', 'slug': 'home-kitchen'},
    {'name': 'Sports', 'slug': 'sports'},
]

PRODUCTS = [
    {'name': 'Wireless Noise-Cancelling Headphones', 'slug': 'wireless-headphones', 'category': 'electronics', 'price': '8999', 'compare_price': '12999', 'stock': 50, 'is_featured': True, 'description': 'Premium over-ear headphones with 30h battery and ANC technology.'},
    {'name': 'Mechanical Keyboard TKL', 'slug': 'mechanical-keyboard', 'category': 'electronics', 'price': '4499', 'compare_price': '5999', 'stock': 30, 'is_featured': True, 'description': 'Tenkeyless mechanical keyboard with tactile brown switches and RGB backlighting.'},
    {'name': 'USB-C 65W Fast Charger', 'slug': 'usb-c-charger', 'category': 'electronics', 'price': '1299', 'compare_price': '1799', 'stock': 100, 'is_featured': False, 'description': 'GaN technology 65W fast charger compatible with all USB-C devices.'},
    {'name': 'Smart Watch Series 5', 'slug': 'smart-watch', 'category': 'electronics', 'price': '14999', 'compare_price': '19999', 'stock': 20, 'is_featured': True, 'description': 'Health tracking, GPS, notifications and 7-day battery life.'},
    {'name': 'Classic White Tee', 'slug': 'classic-white-tee', 'category': 'clothing', 'price': '599', 'compare_price': '999', 'stock': 200, 'is_featured': False, 'description': '100% organic cotton premium crew neck t-shirt.'},
    {'name': 'Slim Fit Chinos', 'slug': 'slim-fit-chinos', 'category': 'clothing', 'price': '1799', 'compare_price': '2499', 'stock': 80, 'is_featured': True, 'description': 'Stretch cotton slim fit chinos in 8 colours.'},
    {'name': 'Wool Blend Overcoat', 'slug': 'wool-overcoat', 'category': 'clothing', 'price': '5999', 'compare_price': '8999', 'stock': 25, 'is_featured': False, 'description': 'Italian wool blend overcoat with double-breasted buttons.'},
    {'name': 'Atomic Habits — James Clear', 'slug': 'atomic-habits', 'category': 'books', 'price': '499', 'compare_price': '699', 'stock': 150, 'is_featured': True, 'description': 'The #1 New York Times bestseller on building good habits.'},
    {'name': 'Deep Work — Cal Newport', 'slug': 'deep-work', 'category': 'books', 'price': '449', 'compare_price': '599', 'stock': 120, 'is_featured': False, 'description': 'Rules for focused success in a distracted world.'},
    {'name': 'The Psychology of Money', 'slug': 'psychology-of-money', 'category': 'books', 'price': '399', 'compare_price': '550', 'stock': 180, 'is_featured': True, 'description': 'Timeless lessons on wealth, greed, and happiness.'},
    {'name': 'Stainless Steel Water Bottle 1L', 'slug': 'steel-water-bottle', 'category': 'home-kitchen', 'price': '799', 'compare_price': '1299', 'stock': 90, 'is_featured': False, 'description': 'Double-walled insulated bottle keeps drinks cold for 24h.'},
    {'name': 'Non-Stick Cookware Set 5pc', 'slug': 'nonstick-cookware', 'category': 'home-kitchen', 'price': '2999', 'compare_price': '4499', 'stock': 40, 'is_featured': True, 'description': 'PFOA-free ceramic non-stick cookware set with glass lids.'},
    {'name': 'Air Purifier HEPA H13', 'slug': 'air-purifier', 'category': 'home-kitchen', 'price': '7999', 'compare_price': '10999', 'stock': 15, 'is_featured': True, 'description': 'True HEPA H13 filter for rooms up to 400 sq ft, covers 99.97% pollutants.'},
    {'name': 'Yoga Mat Premium 6mm', 'slug': 'yoga-mat', 'category': 'sports', 'price': '1499', 'compare_price': '2299', 'stock': 60, 'is_featured': False, 'description': 'Eco-friendly TPE yoga mat with alignment lines and carrying strap.'},
    {'name': 'Resistance Bands Set (5 levels)', 'slug': 'resistance-bands', 'category': 'sports', 'price': '899', 'compare_price': '1299', 'stock': 110, 'is_featured': True, 'description': 'Latex-free resistance bands from 5lb to 50lb for home workouts.'},
    {'name': 'Adjustable Dumbbell 20kg', 'slug': 'adjustable-dumbbell', 'category': 'sports', 'price': '4999', 'compare_price': '6999', 'stock': 18, 'is_featured': True, 'description': 'Quick-adjust dial system, replaces 15 dumbbells in one.'},
    {'name': 'Wireless Earbuds TWS', 'slug': 'wireless-earbuds', 'category': 'electronics', 'price': '2999', 'compare_price': '4999', 'stock': 75, 'is_featured': True, 'description': 'True wireless earbuds with 28h total playback and IPX5 water resistance.'},
    {'name': 'Portable Bluetooth Speaker', 'slug': 'bluetooth-speaker', 'category': 'electronics', 'price': '3499', 'compare_price': '4999', 'stock': 45, 'is_featured': False, 'description': '360° sound, 20h battery, waterproof speaker for outdoors.'},
    {'name': 'Running Shoes Pro', 'slug': 'running-shoes', 'category': 'sports', 'price': '3999', 'compare_price': '5499', 'stock': 55, 'is_featured': True, 'description': 'Lightweight responsive foam running shoes for daily training.'},
    {'name': 'Coffee Maker Drip 12-Cup', 'slug': 'coffee-maker', 'category': 'home-kitchen', 'price': '3299', 'compare_price': '4499', 'stock': 22, 'is_featured': False, 'description': 'Programmable 12-cup drip coffee maker with thermal carafe.'},
]


class Command(BaseCommand):
    help = 'Seed the database with demo categories, products, and an admin user'

    def handle(self, *args, **kwargs):
        # Create admin user
        if not User.objects.filter(email='admin@shopkart.com').exists():
            admin = User.objects.create_superuser(
                email='admin@shopkart.com',
                username='admin',
                password='Admin@1234',
                first_name='Admin',
                last_name='User',
                is_seller=True,
            )
            self.stdout.write(self.style.SUCCESS('Created admin user: admin@shopkart.com / Admin@1234'))
        else:
            admin = User.objects.get(email='admin@shopkart.com')

        # Create categories
        cat_map = {}
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            cat_map[cat_data['slug']] = cat
            if created:
                self.stdout.write(f'  Category: {cat.name}')

        # Create products
        count = 0
        for p in PRODUCTS:
            if not Product.objects.filter(slug=p['slug']).exists():
                Product.objects.create(
                    seller=admin,
                    category=cat_map[p['category']],
                    name=p['name'],
                    slug=p['slug'],
                    description=p['description'],
                    price=Decimal(p['price']),
                    compare_price=Decimal(p['compare_price']),
                    stock=p['stock'],
                    is_featured=p['is_featured'],
                    is_active=True,
                    sku=f"SKU-{p['slug'].upper()[:12]}",
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Seeded {count} products across {len(CATEGORIES)} categories.'))
        self.stdout.write(self.style.WARNING('Note: Product images are not included. Add them via Django Admin.'))
