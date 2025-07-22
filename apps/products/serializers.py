from rest_framework import serializers
from .models import (
    Product, ProductImage, ProductVideo, Category, 
    SubCategory, Brand, Platform, Tag
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at', 'active']


class SubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'slug', 'category', 'category_name', 'created_at', 'updated_at', 'active']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at', 'active']


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at', 'active']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at', 'active']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_featured', 'order', 'created_at', 'updated_at']


class ProductVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = ['id', 'video', 'title', 'is_featured', 'order', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    sub_category_name = serializers.CharField(source='sub_category.name', read_only=True)
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    featured_image = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_asin', 'title', 'slug', 'price', 'regular_price',
            'discount_percent', 'savings_percent', 'rating', 'brand_name',
            'category_name', 'sub_category_name', 'platform_name', 'featured_image',
            'tags', 'featured', 'created_at', 'updated_at'
        ]

    def get_featured_image(self, obj):
        featured_img = obj.images.filter(is_featured=True).first()
        if featured_img:
            return ProductImageSerializer(featured_img).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual product views"""
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    sub_category = SubCategorySerializer(read_only=True)
    platform = PlatformSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)
    featured_image = serializers.SerializerMethodField()
    featured_video = serializers.SerializerMethodField()
    
    # Price info as nested object
    price_info = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_asin', 'title', 'slug', 'description',
            'price_info', 'rating', 'brand', 'platform', 'category', 
            'sub_category', 'tags', 'shipping', 'returns',
            'images', 'videos', 'featured_image', 'featured_video',
            'featured', 'published', 'active', 'created_at', 'updated_at'
        ]

    def get_featured_image(self, obj):
        featured_img = obj.images.filter(is_featured=True).first()
        if featured_img:
            return ProductImageSerializer(featured_img).data
        return None

    def get_featured_video(self, obj):
        featured_vid = obj.videos.filter(is_featured=True).first()
        if featured_vid:
            return ProductVideoSerializer(featured_vid).data
        return None

    def get_price_info(self, obj):
        return {
            'price': f"${obj.price}",
            'regular_price': f"${obj.regular_price}" if obj.regular_price else None,
            'cost_savings': float(obj.cost_savings) if obj.cost_savings else None,
            'discount_percent': obj.discount_percent,
            'savings_percent': obj.savings_percent
        }


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating products"""
    images_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    videos_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'product_asin', 'title', 'description', 'price', 'regular_price',
            'cost_savings', 'discount_percent', 'savings_percent', 'rating',
            'brand', 'platform', 'category', 'sub_category', 'shipping',
            'returns', 'featured', 'published', 'active', 'images_data',
            'videos_data', 'tag_ids'
        ]

    def create(self, validated_data):
        images_data = validated_data.pop('images_data', [])
        videos_data = validated_data.pop('videos_data', [])
        tag_ids = validated_data.pop('tag_ids', [])
        
        product = Product.objects.create(**validated_data)
        
        # Add tags
        if tag_ids:
            product.tags.set(tag_ids)
        
        # Add images
        for i, image_data in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                order=i,
                **image_data
            )
        
        # Add videos
        for i, video_data in enumerate(videos_data):
            ProductVideo.objects.create(
                product=product,
                order=i,
                **video_data
            )
        
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images_data', None)
        videos_data = validated_data.pop('videos_data', None)
        tag_ids = validated_data.pop('tag_ids', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        
        # Update images if provided
        if images_data is not None:
            instance.images.all().delete()
            for i, image_data in enumerate(images_data):
                ProductImage.objects.create(
                    product=instance,
                    order=i,
                    **image_data
                )
        
        # Update videos if provided
        if videos_data is not None:
            instance.videos.all().delete()
            for i, video_data in enumerate(videos_data):
                ProductVideo.objects.create(
                    product=instance,
                    order=i,
                    **video_data
                )
        
        return instance

    def to_representation(self, instance):
        return ProductDetailSerializer(instance, context=self.context).data