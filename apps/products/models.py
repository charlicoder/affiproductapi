from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    slug = models.SlugField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Sub Categories"
        unique_together = ['name', 'category']
        ordering = ['name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_asin = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    description = models.TextField()
    
    # SEO and Meta Fields
    page_header = models.CharField(max_length=255, blank=True, null=True, help_text="SEO-optimized page header")
    meta_description = models.TextField(max_length=160, blank=True, null=True, help_text="Meta description for search engines")
    meta_keywords = models.CharField(max_length=500, blank=True, null=True, help_text="Comma-separated keywords for SEO")
    open_graph_meta_description = models.TextField(max_length=200, blank=True, null=True, help_text="Description for social media sharing")
    
    # Product Details
    product_features = models.JSONField(default=list, blank=True, help_text="List of product features")
    product_tags = models.CharField(max_length=500, blank=True, null=True, help_text="Social media hashtags and tags")
    
    # Price information
    price = models.DecimalField(max_digits=10, decimal_places=2)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_savings = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_percent = models.CharField(max_length=10, null=True, blank=True)
    savings_percent = models.CharField(max_length=10, null=True, blank=True)
    
    # Rating
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        null=True, 
        blank=True
    )
    
    # Relationships
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    
    # Shipping and returns
    shipping = models.CharField(max_length=200, null=True, blank=True)
    returns = models.CharField(max_length=200, null=True, blank=True)
    
    # Status fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['product_asin']),
            models.Index(fields=['brand']),
            models.Index(fields=['category']),
            models.Index(fields=['sub_category']),
            models.Index(fields=['published', 'active']),
        ]

    def __str__(self):
        return self.title[:100]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def featured_image(self):
        featured_img = self.images.filter(is_featured=True).first()
        return featured_img.image if featured_img else None

    @property
    def featured_video(self):
        featured_vid = self.videos.filter(is_featured=True).first()
        return featured_vid.video if featured_vid else None

    @property
    def formatted_features(self):
        """Return product features as a formatted string"""
        if self.product_features:
            return ', '.join(self.product_features)
        return ''

    @property
    def meta_keywords_list(self):
        """Return meta keywords as a list"""
        if self.meta_keywords:
            return [keyword.strip() for keyword in self.meta_keywords.split(',')]
        return []


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-is_featured', 'created_at']

    def __str__(self):
        return f"{self.product.title[:50]} - Image {self.id}"

    def save(self, *args, **kwargs):
        # Ensure only one featured image per product
        if self.is_featured:
            ProductImage.objects.filter(
                product=self.product, 
                is_featured=True
            ).exclude(id=self.id).update(is_featured=False)
        super().save(*args, **kwargs)


class ProductVideo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos')
    video = models.URLField(max_length=500)
    title = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-is_featured', 'created_at']

    def __str__(self):
        return f"{self.product.title[:50]} - Video {self.id}"

    def save(self, *args, **kwargs):
        # Ensure only one featured video per product
        if self.is_featured:
            ProductVideo.objects.filter(
                product=self.product, 
                is_featured=True
            ).exclude(id=self.id).update(is_featured=False)
        super().save(*args, **kwargs)