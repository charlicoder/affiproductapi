from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    CategoryViewSet,
    SubCategoryViewSet,
    BrandViewSet,
    PlatformViewSet,
    TagViewSet,
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"subcategories", SubCategoryViewSet, basename="subcategory")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"platforms", PlatformViewSet, basename="platform")
router.register(r"tags", TagViewSet, basename="tag")

app_name = "products"

urlpatterns = [
    path("", include(router.urls)),
    # Alternative URL patterns for SEO-friendly URLs
    path(
        "products/slug/<slug:slug>/",
        ProductViewSet.as_view({"get": "retrieve"}),
        name="product-detail-slug",
    ),
]
