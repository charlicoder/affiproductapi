# management/commands/create_sample_data.py
# Create this file in products/management/commands/ directory

from django.core.management.base import BaseCommand
from apps.products.models import (
    Product, ProductImage, ProductVideo, Category, 
    SubCategory, Brand, Platform, Tag
)


class Command(BaseCommand):
    help = 'Create sample data for products'

    def handle(self, *args, **options):
        # Create Category
        personal_care, created = Category.objects.get_or_create(
            name="Personal Care",
            defaults={'active': True}
        )
        
        # Create SubCategory
        oral_care, created = SubCategory.objects.get_or_create(
            name="Oral Care",
            category=personal_care,
            defaults={'active': True}
        )
        
        # Create Brand
        waterpik_brand, created = Brand.objects.get_or_create(
            name="Waterpik",
            defaults={'active': True}
        )
        
        # Create Platform
        amazon_platform, created = Platform.objects.get_or_create(
            name="Amazon",
            defaults={'active': True}
        )
        
        # Create Tags
        tags_data = ["Oral Care", "Dental Floss & Picks", "Power Dental Flossers"]
        tags = []
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'active': True}
            )
            tags.append(tag)
        
        # Create Product
        product, created = Product.objects.get_or_create(
            product_asin="B01LXY19XD",
            defaults={
                'title': "Waterpik Aquarius Water Flosser For Teeth Cleaning, Gums, Braces, Dental Care, Electric Power With 10 Settings, 7 Tips For Multiple Users And Needs, ADA Accepted, Black WP-662, Packaging May Vary",
                'description': "The Waterpik Aquarius water flosser features a compact, contemporary design and advanced water flossing technology for maximum performance. It comes with 7 flossing tips for a variety of dental needs and multiple users, a convenient one-minute timer with 30-second pacer to ensure thorough water flossing of all areas, and a removable water reservoir with 90+ seconds of flossing time. The special 360-degree rotating tip handle easily reaches your whole mouth, even back teeth. The Waterpik Aquarius water flosser removes up to 99.9% of plaque bacteria that causes gingivitis, cavities, and bad breath from treated areas and is clinically proven up to 2X as effective as string floss for removing bacterial plaque and improving gum health. Waterpik is the #1 water flosser brand recommended by dental professionals, and the Waterpik Aquarius water flosser is accepted by the American Dental Association (ADA) for safety and effectiveness. Backed by a 3-year manufacturer's limited warranty, see product manual for details.",
                'price': 87.90,
                'regular_price': 99.99,
                'cost_savings': 12.00,
                'discount_percent': "-12%",
                'savings_percent': "12%",
                'rating': 4.6,
                'brand': waterpik_brand,
                'platform': amazon_platform,
                'category': personal_care,
                'sub_category': oral_care,
                'shipping': "$5.79 Import Charges & FREE Shipping to Qatar",
                'returns': "FREE International Returns",
                'featured': True,
                'published': True,
                'active': True
            }
        )
        
        if created:
            # Add tags to product
            product.tags.set(tags)
            
            # Create Product Image
            ProductImage.objects.create(
                product=product,
                image="https://m.media-amazon.com/images/I/51FWqFdc30L._SX300_SY300_QL70_ML2_.jpg",
                alt_text="Waterpik Aquarius Water Flosser",
                is_featured=True,
                order=0
            )
            
            # Create Product Videos
            video_urls = [
                "https://m.media-amazon.com/images/S/al-na-9d5791cf-3faf/94c92c0c-cfa6-4df4-82db-c1fcb08275cc.mp4/productVideoOptimized.mp4",
                "https://m.media-amazon.com/images/S/al-na-9d5791cf-3faf/d1ecf3ca-8542-4613-a7af-67d5af912fd3.mp4/productVideoOptimized.mp4",
                "https://m.media-amazon.com/images/S/al-na-9d5791cf-3faf/c9a027cc-aee0-49da-9ab8-4274abcdd9ce.mp4/productVideoOptimized.mp4",
                "https://m.media-amazon.com/images/S/al-na-9d5791cf-3faf/9cbf057f-c959-4b45-8833-54afc2f21228.mp4/productVideoOptimized.mp4",
                "https://m.media-amazon.com/images/S/al-na-9d5791cf-3faf/1b8fc326-fcd2-43ad-a96c-98792b622ccb.mp4/productVideoOptimized.mp4"
            ]
            
            for i, video_url in enumerate(video_urls):
                ProductVideo.objects.create(
                    product=product,
                    video=video_url,
                    title=f"Waterpik Aquarius Demo Video {i+1}",
                    is_featured=(i == 0),  # First video is featured
                    order=i
                )
            
            self.stdout.write(
                self.style.SUCCESS('Successfully created sample product data!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Product with ASIN B01LXY19XD already exists!')
            )