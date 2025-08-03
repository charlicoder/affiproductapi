from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Product,
    ProductImage,
    ProductVideo,
    Category,
    SubCategory,
    Brand,
    Platform,
    Tag,
)


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 0
    fields = ("name", "slug", "active")
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ("image_preview", "image", "alt_text", "is_featured", "order")
    readonly_fields = ("image_preview",)
    ordering = ("order", "-is_featured")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 5px;" />',
                obj.image,
            )
        return "No Image"

    image_preview.short_description = "Preview"


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 0
    fields = ("video_preview", "video", "title", "is_featured", "order")
    readonly_fields = ("video_preview",)
    ordering = ("order", "-is_featured")

    def video_preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="200" height="100" controls style="border-radius: 5px;">'
                '<source src="{}" type="video/mp4">'
                "Your browser does not support the video tag."
                "</video>",
                obj.video,
            )
        return "No Video"

    video_preview.short_description = "Preview"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "product_count", "active", "created_at"]
    list_filter = ["active", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubCategoryInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(product_count=Count("products", distinct=True))
        return queryset

    def product_count(self, obj):
        return obj.product_count

    product_count.admin_order_field = "product_count"
    product_count.short_description = "Products"


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "slug", "product_count", "active", "created_at"]
    list_filter = ["category", "active", "created_at"]
    search_fields = ["name", "category__name"]
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("category").annotate(
            product_count=Count("products", distinct=True)
        )
        return queryset

    def product_count(self, obj):
        return obj.product_count

    product_count.admin_order_field = "product_count"
    product_count.short_description = "Products"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "product_count", "active", "created_at"]
    list_filter = ["active", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(product_count=Count("products", distinct=True))
        return queryset

    def product_count(self, obj):
        return obj.product_count

    product_count.admin_order_field = "product_count"
    product_count.short_description = "Products"


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "product_count", "active", "created_at"]
    list_filter = ["active", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(product_count=Count("products", distinct=True))
        return queryset

    def product_count(self, obj):
        return obj.product_count

    product_count.admin_order_field = "product_count"
    product_count.short_description = "Products"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "product_count", "active", "created_at"]
    list_filter = ["active", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(product_count=Count("products", distinct=True))
        return queryset

    def product_count(self, obj):
        return obj.product_count

    product_count.admin_order_field = "product_count"
    product_count.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "title_short",
        "product_asin",
        "view_product",
        "brand",
        "category",
        "sub_category",
        "price",
        "rating",
        "featured_image_preview",
        "featured",
        "published",
        "active",
        "created_at",
    ]
    list_filter = [
        "brand",
        "category",
        "sub_category",
        "platform",
        "featured",
        "published",
        "active",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "title",
        "product_asin",
        "description",
        "brand__name",
        "category__name",
        "sub_category__name",
    ]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    list_per_page = 20  # Set pagination to 20 items per page

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("product_asin", "title", "slug", "description")},
        ),
        (
            "Categorization",
            {"fields": ("brand", "category", "sub_category", "platform", "tags")},
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "regular_price",
                    "cost_savings",
                    "discount_percent",
                    "savings_percent",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Product Details",
            {"fields": ("rating", "shipping", "returns"), "classes": ("collapse",)},
        ),
        ("Status", {"fields": ("featured", "published", "active")}),
    )

    inlines = [ProductImageInline, ProductVideoInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            "brand", "category", "sub_category", "platform"
        ).prefetch_related("images", "videos")
        return queryset

    def view_product(self, obj):
        if obj.af_link:
            return format_html(
                '<a href="{}" target="_blank" style="color: #007cba; text-decoration: none;">View Product</a>',
                obj.af_link,
            )
        return "No Link"

    view_product.short_description = "Link"

    def title_short(self, obj):
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title

    title_short.short_description = "Title"

    def featured_image_preview(self, obj):
        featured_img = obj.images.filter(is_featured=True).first()
        if featured_img:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                featured_img.image,
            )
        return "No Featured Image"

    featured_image_preview.short_description = "Image"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(active=True)
        elif db_field.name == "sub_category":
            kwargs["queryset"] = SubCategory.objects.filter(active=True).select_related(
                "category"
            )
        elif db_field.name == "brand":
            kwargs["queryset"] = Brand.objects.filter(active=True)
        elif db_field.name == "platform":
            kwargs["queryset"] = Platform.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "tags":
            kwargs["queryset"] = Tag.objects.filter(active=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # Custom admin actions
    actions = [
        "make_featured",
        "remove_featured",
        "publish",
        "unpublish",
        "activate",
        "deactivate",
    ]

    def make_featured(self, request, queryset):
        queryset.update(featured=True)
        self.message_user(request, f"{queryset.count()} products marked as featured.")

    make_featured.short_description = "Mark selected products as featured"

    def remove_featured(self, request, queryset):
        queryset.update(featured=False)
        self.message_user(
            request, f"{queryset.count()} products removed from featured."
        )

    remove_featured.short_description = "Remove selected products from featured"

    def publish(self, request, queryset):
        queryset.update(published=True)
        self.message_user(request, f"{queryset.count()} products published.")

    publish.short_description = "Publish selected products"

    def unpublish(self, request, queryset):
        queryset.update(published=False)
        self.message_user(request, f"{queryset.count()} products unpublished.")

    unpublish.short_description = "Unpublish selected products"

    def activate(self, request, queryset):
        queryset.update(active=True)
        self.message_user(request, f"{queryset.count()} products activated.")

    activate.short_description = "Activate selected products"

    def deactivate(self, request, queryset):
        queryset.update(active=False)
        self.message_user(request, f"{queryset.count()} products deactivated.")

    deactivate.short_description = "Deactivate selected products"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = [
        "product_title",
        "image_preview",
        "is_featured",
        "order",
        "created_at",
    ]
    list_filter = ["is_featured", "created_at"]
    search_fields = ["product__title", "alt_text"]

    def product_title(self, obj):
        return (
            obj.product.title[:50] + "..."
            if len(obj.product.title) > 50
            else obj.product.title
        )

    product_title.short_description = "Product"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 5px;" />',
                obj.image,
            )
        return "No Image"

    image_preview.short_description = "Preview"


@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    list_display = [
        "product_title",
        "title",
        "video_preview",
        "is_featured",
        "order",
        "created_at",
    ]
    list_filter = ["is_featured", "created_at"]
    search_fields = ["product__title", "title"]

    def product_title(self, obj):
        return (
            obj.product.title[:50] + "..."
            if len(obj.product.title) > 50
            else obj.product.title
        )

    product_title.short_description = "Product"

    def video_preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="150" height="75" controls style="border-radius: 5px;">'
                '<source src="{}" type="video/mp4">'
                "Your browser does not support the video tag."
                "</video>",
                obj.video,
            )
        return "No Video"

    video_preview.short_description = "Preview"
