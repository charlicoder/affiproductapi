import json
import os
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.products.models import (
    Product, Brand, Platform, Category, SubCategory, Tag,
    ProductImage, ProductVideo
)


class Command(BaseCommand):
    help = 'Upload products from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to the JSON file containing product data'
        )
        parser.add_argument(
            '--platform',
            type=str,
            default='Amazon',
            help='Platform name (default: Amazon)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing products if they exist'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating it'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        platform_name = options['platform']
        update_existing = options['update']
        dry_run = options['dry_run']

        if not os.path.exists(json_file):
            raise CommandError(f'File "{json_file}" does not exist.')

        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON file: {e}')

        if not isinstance(data, list):
            raise CommandError('JSON file should contain a list of products')

        self.stdout.write(f"Found {len(data)} products to process")

        # Get or create platform
        platform, created = Platform.objects.get_or_create(
            name=platform_name,
            defaults={'active': True}
        )
        if created and not dry_run:
            self.stdout.write(f"Created platform: {platform.name}")

        success_count = 0
        error_count = 0

        for index, product_data in enumerate(data, 1):
            try:
                if dry_run:
                    self.stdout.write(f"[DRY RUN] Would process product {index}: {product_data.get('title', 'Unknown')}")
                else:
                    with transaction.atomic():
                        self.process_product(product_data, platform, update_existing)
                        success_count += 1
                        self.stdout.write(f"✓ Processed product {index}: {product_data.get('title', 'Unknown')}")
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"✗ Error processing product {index}: {str(e)}")
                )

        # Summary
        if dry_run:
            self.stdout.write(f"\n[DRY RUN] Would process {len(data)} products")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n✓ Successfully processed: {success_count}")
            )
            if error_count > 0:
                self.stdout.write(
                    self.style.ERROR(f"✗ Errors: {error_count}")
                )

    def process_product(self, data, platform, update_existing):
        """Process a single product from JSON data"""
        
        # Extract basic info
        product_asin = data.get('product_asin', '').strip()
        if not product_asin:
            raise ValueError("Product ASIN is required")

        title = data.get('title', '').strip()
        if not title:
            raise ValueError("Product title is required")

        # Check if product exists
        product_exists = Product.objects.filter(product_asin=product_asin).exists()
        if product_exists and not update_existing:
            raise ValueError(f"Product with ASIN {product_asin} already exists. Use --update to update existing products.")

        # Get or create Brand
        brand_data = data.get('brand', {})
        brand_name = brand_data.get('brand_name', '').strip() if brand_data else 'Unknown'
        brand_url = brand_data.get('brand_url', '') if brand_data else ''
        
        brand, _ = Brand.objects.get_or_create(
            name=brand_name,
            defaults={
                'url': brand_url,
                'active': True
            }
        )

        # Get or create Category
        category_name = data.get('category', 'Uncategorized').strip()
        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={'active': True}
        )

        # Get or create SubCategory
        sub_category_name = data.get('sub_category', 'General').strip()
        sub_category, _ = SubCategory.objects.get_or_create(
            name=sub_category_name,
            category=category,
            defaults={'active': True}
        )

        # Parse price information
        price_info = data.get('price_info', {})
        price = self.parse_price(price_info.get('price', '0'))
        regular_price = self.parse_price(price_info.get('regular_price', '')) if price_info.get('regular_price') else None
        cost_savings = self.parse_price(price_info.get('cost_savings', '')) if price_info.get('cost_savings') else None

        # Parse rating
        rating_str = data.get('rating', '')
        rating = None
        if rating_str:
            try:
                rating = Decimal(str(rating_str))
                if rating < 0 or rating > 5:
                    rating = None
            except (InvalidOperation, ValueError):
                rating = None

        # Prepare product data
        product_data = {
            'product_asin': product_asin,
            'title': title,
            'description': data.get('description', ''),
            'price': price,
            'regular_price': regular_price,
            'cost_savings': cost_savings,
            'discount_percent': price_info.get('discount_percent', ''),
            'savings_percent': price_info.get('savings_percent', ''),
            'rating': rating,
            'brand': brand,
            'platform': platform,
            'category': category,
            'sub_category': sub_category,
            'shipping': data.get('shipping', ''),
            'returns': data.get('returns', ''),
            'published': True,
            'active': True,
            'featured': False,
            # SEO and Meta fields
            'page_header': data.get('page_header', ''),
            'meta_description': data.get('meta_description', ''),
            'meta_keywords': data.get('meta_keywords', ''),
            'open_graph_meta_description': data.get('open_graph_meta_description', ''),
            'product_features': data.get('product_features', []),
            'product_tags': data.get('product_tags', ''),
        }

        # Create or update product
        if product_exists and update_existing:
            product = Product.objects.get(product_asin=product_asin)
            for key, value in product_data.items():
                setattr(product, key, value)
            product.save()
        else:
            product = Product.objects.create(**product_data)

        # Handle tags
        tag_names = data.get('tags', [])
        if tag_names:
            tags = []
            for tag_name in tag_names:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={'active': True}
                    )
                    tags.append(tag)
            product.tags.set(tags)

        # Handle images
        self.process_images(product, data.get('images', []), update_existing)

        # Handle videos
        self.process_videos(product, data.get('videos', []), update_existing)

        return product

    def process_images(self, product, image_urls, update_existing):
        """Process product images"""
        if update_existing:
            # Remove existing images
            product.images.all().delete()

        for index, image_url in enumerate(image_urls):
            if image_url.strip():
                ProductImage.objects.create(
                    product=product,
                    image=image_url.strip(),
                    is_featured=(index == 0),  # First image is featured
                    order=index,
                    alt_text=f"{product.title} - Image {index + 1}"
                )

    def process_videos(self, product, video_urls, update_existing):
        """Process product videos"""
        if update_existing:
            # Remove existing videos
            product.videos.all().delete()

        for index, video_url in enumerate(video_urls):
            if video_url.strip():
                ProductVideo.objects.create(
                    product=product,
                    video=video_url.strip(),
                    is_featured=(index == 0),  # First video is featured
                    order=index,
                    title=f"{product.title} - Video {index + 1}"
                )

    def parse_price(self, price_str):
        """Parse price string and return Decimal"""
        if not price_str:
            return Decimal('0.00')
        
        # Remove currency symbols and spaces
        price_clean = str(price_str).replace('$', '').replace(',', '').strip()
        
        try:
            return Decimal(price_clean)
        except (InvalidOperation, ValueError):
            return Decimal('0.00')