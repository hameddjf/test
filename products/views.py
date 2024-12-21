import re

from django.db.models import Q
from django.db.models import Count, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from .models import Category, Product, ProductGallery, MostViewed
from .serializers import CategorySerializer, ProductSerializer, ProductDetailSerializer, ProductGallerySerializer, ProductSearchSerializer


class CategoryListCreateAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailAPIView(APIView):
    def get_object(self, slug):
        return get_object_or_404(Category, slug=slug)

    def get(self, request, slug):
        category = self.get_object(slug)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, slug):
        category = self.get_object(slug)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        category = self.get_object(slug)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductGalleryListCreateAPIView(APIView):
    def get(self, request):
        product_id = request.query_params.get('product_id')
        if product_id:
            galleries = ProductGallery.objects.filter(product_id=product_id)
        else:
            galleries = ProductGallery.objects.all()
        serializer = ProductGallerySerializer(galleries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductGallerySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 12

    def get_paginated_response(self, data):
        return Response({
            'current_page': self.page.number,
            'per_page': self.page.paginator.per_page,
            'total_pages': self.page.paginator.num_pages,
            'total_products': self.page.paginator.count,
            'products': data
        })

class ProductListCreateAPIView(APIView):
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Product.objects.all()
        view_count_subquery = MostViewed.objects.filter(product=OuterRef('pk')) \
            .values('product') \
            .annotate(count=Count('id')) \
            .values('count')
        return queryset.annotate(view_count_annotation=Subquery(view_count_subquery))

    def get(self, request):
        paginator = self.pagination_class()
        
        queryset = self.get_queryset()
        
        category = request.query_params.get('category')
        ordering = request.query_params.get('ordering', '-created')
        
        if category:
            queryset = queryset.filter(category__slug=category)
        
        queryset = queryset.order_by(ordering)
        
        page = paginator.paginate_queryset(queryset, request)
        
        serializer = ProductSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailAPIView(APIView):
    def get_object(self, slug):
        return get_object_or_404(
            Product.objects.prefetch_related(
                'productgallery_set'
            ).select_related('category'),
            slug=slug
        )

    def get(self, request, slug):
        product = self.get_object(slug)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)

    def put(self, request, slug):
        product = self.get_object(slug)
        serializer = ProductDetailSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        product = self.get_object(slug)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class ProductSingleAPIView(APIView):
    def get(self, request, slug):
        product = get_object_or_404(
            Product.objects.prefetch_related(
                'productgallery_set'
            ).select_related('category'),
            slug=slug
        )
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)


# search vectore


class ProductSearchView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = ProductSearchSerializer

    def get_text_similarity(self, text1, text2):
        """محاسبه شباهت متنی ساده"""
        text1 = re.sub(r'[^\w\s]', '', text1.lower())
        text2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0
        return intersection / union

    def post(self, request):
        query = request.data.get('query', '').strip()
        top_k = min(int(request.data.get('top_k', 10)), 100)
        category_id = request.data.get('category_id')

        if not query:
            return Response({
                'error': 'جستجو نمی‌تواند خالی باشد'
            }, status=400)

        base_queryset = Product.objects.all()
        if category_id:
            base_queryset = base_queryset.filter(category_id=category_id)

        products = base_queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

        if not products.exists():
            return Response([])

        results = []
        for product in products:
            product_text = f"{product.title} {product.description}"
            
            similarity = self.get_text_similarity(query, product_text)
            
            if query.lower() in product.title.lower():
                similarity += 0.3
            
            results.append({
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'category': product.category.name,
                'similarity': round(similarity, 3)
            })

        results.sort(key=lambda x: x['similarity'], reverse=True)
        results = results[:top_k]

        return Response(results)
