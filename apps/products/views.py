from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import (
    Product, Category, SubCategory, Brand, Platform, Tag
)
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    CategorySerializer, SubCategorySerializer, BrandSerializer, 
    PlatformSerializer, TagSerializer
)


class ProductFilter:
    """Custom filter class for products"""
    
    @staticmethod
    def filter_queryset(queryset, query_params):
        # Search functionality
        search = query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__name__icontains=search) |
                Q(category__name__icontains=search) |
                Q(sub_category__name__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()
        
        # Filter by brand
        brand = query_params.get('brand')
        if brand:
            queryset = queryset.filter(
                Q(brand__name__iexact=brand) |
                Q(brand__slug__iexact=brand)
            )
        
        # Filter by category
        category = query_params.get('category')
        if category:
            queryset = queryset.filter(
                Q(category__name__iexact=category) |
                Q(category__slug__iexact=category)
            )
        
        # Filter by subcategory
        subcategory = query_params.get('subcategory')
        if subcategory:
            queryset = queryset.filter(
                Q(sub_category__name__iexact=subcategory) |
                Q(sub_category__slug__iexact=subcategory)
            )
        
        # Filter by platform
        platform = query_params.get('platform')
        if platform:
            queryset = queryset.filter(
                Q(platform__name__iexact=platform) |
                Q(platform__slug__iexact=platform)
            )
        
        # Filter by tags
        tags = query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(
                tags__name__in=tag_list
            ).distinct()
        
        # Filter by featured status
        featured = query_params.get('featured')
        if featured is not None:
            queryset = queryset.filter(featured=featured.lower() == 'true')
        
        # Filter by published status
        published = query_params.get('published')
        if published is not None:
            queryset = queryset.filter(published=published.lower() == 'true')
        
        # Filter by active status
        active = query_params.get('active')
        if active is not None:
            queryset = queryset.filter(active=active.lower() == 'true')
        
        # Price range filtering
        min_price = query_params.get('min_price')
        max_price = query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Rating filtering
        min_rating = query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product operations
    """
    queryset = Product.objects.select_related(
        'brand', 'category', 'sub_category', 'platform'
    ).prefetch_related('tags', 'images', 'videos').filter(
        published=True, active=True
    )
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'updated_at', 'price', 'rating', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        queryset = self.queryset
        return ProductFilter.filter_queryset(queryset, self.request.query_params)

    def retrieve(self, request, pk=None):
        """Get product by ID or slug"""
        try:
            if pk.replace('-', '').replace('_', '').isalnum() and len(pk) > 10:
                # Likely a slug
                product = get_object_or_404(self.get_queryset(), slug=pk)
            else:
                # Likely an ID
                product = get_object_or_404(self.get_queryset(), pk=pk)
            
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        queryset = self.get_queryset().filter(featured=True)
        queryset = ProductFilter.filter_queryset(queryset, request.query_params)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_slug>[^/.]+)')
    def by_category(self, request, category_slug=None):
        """Get products by category"""
        queryset = self.get_queryset().filter(
            Q(category__slug=category_slug) | Q(category__name__iexact=category_slug)
        )
        queryset = ProductFilter.filter_queryset(queryset, request.query_params)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-subcategory/(?P<subcategory_slug>[^/.]+)')
    def by_subcategory(self, request, subcategory_slug=None):
        """Get products by subcategory"""
        queryset = self.get_queryset().filter(
            Q(sub_category__slug=subcategory_slug) | 
            Q(sub_category__name__iexact=subcategory_slug)
        )
        queryset = ProductFilter.filter_queryset(queryset, request.query_params)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-brand/(?P<brand_slug>[^/.]+)')
    def by_brand(self, request, brand_slug=None):
        """Get products by brand"""
        queryset = self.get_queryset().filter(
            Q(brand__slug=brand_slug) | Q(brand__name__iexact=brand_slug)
        )
        queryset = ProductFilter.filter_queryset(queryset, request.query_params)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-platform/(?P<platform_slug>[^/.]+)')
    def by_platform(self, request, platform_slug=None):
        """Get products by platform"""
        queryset = self.get_queryset().filter(
            Q(platform__slug=platform_slug) | Q(platform__name__iexact=platform_slug)
        )
        queryset = ProductFilter.filter_queryset(queryset, request.query_params)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Category operations"""
    queryset = Category.objects.filter(active=True)
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """Get subcategories for a category"""
        category = self.get_object()
        subcategories = category.subcategories.filter(active=True)
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response(serializer.data)


class SubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SubCategory operations"""
    queryset = SubCategory.objects.select_related('category').filter(active=True)
    serializer_class = SubCategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'category__name']
    ordering = ['name']


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Brand operations"""
    queryset = Brand.objects.filter(active=True)
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']


class PlatformViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Platform operations"""
    queryset = Platform.objects.filter(active=True)
    serializer_class = PlatformSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Tag operations"""
    queryset = Tag.objects.filter(active=True)
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']
    