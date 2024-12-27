import re

from django.db.models import Q, OuterRef, Subquery, Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db import DatabaseError

from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound, ValidationError

from .models import Category, Product, ProductGallery, MostViewed
from .serializers import CategorySerializer, ProductSerializer, ProductDetailSerializer, ProductGallerySerializer, ProductSearchSerializer


# Category List API View
class CategoryListAPIView(APIView):
    """
    API view to retrieve a list of categories .
    """
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'slug']

    def get(self, request):
        """Retrieve all categories from the database ."""
        try:
            categories = Category.objects.all()
            # category_dict = {category.id: category for category in categories}  # Create a dictionary for quick access
            result = []

            for category in categories:
                if category.parent is None:  
                    serialized_category = CategorySerializer(category).data
                    serialized_category['children'] = []  

                    for child in categories:
                        if child.parent == category:
                            serialized_category['children'].append(CategorySerializer(child).data)

                    result.append(serialized_category)

            return Response(result, status=status.HTTP_200_OK)  # Return the serialized data
        except DatabaseError as db_error:
            return Response({'error': 'Database error occurred: ' + str(db_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except NotFound as nf_error:
            return Response({'error': 'Requested resource not found: ' + str(nf_error)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as val_error:
            return Response({'error': 'Validation error occurred: ' + str(val_error)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class CategoryDetailAPIView(APIView):
#     """
#     API view to retrieve details of a specific category and its related products.
#     """
#     def get_object(self, slug):
#         return get_object_or_404(Category, slug=slug)

#     def get(self, request, slug):
#         try:
#             category = self.get_object(slug)
#             category_serializer = CategorySerializer(category)
            
#             products = Product.objects.filter(category=category)
            
#             paginator = CustomPageNumberPagination()
#             page = paginator.paginate_queryset(products, request)
#             products_serializer = ProductSerializer(page, many=True)

#             return Response({
#                 'category': category_serializer.data,
#                 'products': products_serializer.data
#             }, status=status.HTTP_200_OK)
            
#         except DatabaseError as db_error:
#             return Response({'error': 'Database error occurred: ' + str(db_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             return Response({'error': 'An unexpected error occurred: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Product Gallery List API View
class ProductGalleryListAPIView(APIView):
    """
    API view to retrieve product gallery images.
    """
    def get(self, request):
        product_id = request.query_params.get('product_id')
        try:
            if product_id:
                galleries = ProductGallery.objects.filter(product_id=product_id)
                if not galleries.exists():
                    return Response({'message': 'No galleries found for the specified product.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                galleries = ProductGallery.objects.all()
            
            grouped_galleries = {}
            for gallery in galleries:
                if gallery.product_id not in grouped_galleries:
                    grouped_galleries[gallery.product_id] = []
                grouped_galleries[gallery.product_id].append(gallery)

            response_data = {}
            for product_id, gallery_list in grouped_galleries.items():
                serializer = ProductGallerySerializer(gallery_list, many=True)
                response_data[product_id] = serializer.data

            return Response(response_data, status=status.HTTP_200_OK)

        except DatabaseError as db_error:
            return Response({'error': 'Database error occurred: ' + str(db_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Pagination products
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
        
#  Products
class ProductQuerySet:
    def __init__(self, queryset, error_handler):
        self.queryset = queryset
        self.error_handler = error_handler

    def apply_search(self, search_query):
        if search_query:
            self.queryset = self.queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            ).distinct()
        return self.queryset

    def apply_filters(self, request):
        filters = {
            'category': request.query_params.get('category'),
            'color': request.query_params.get('color'),
            'size': request.query_params.get('size'),
            'min_price': request.query_params.get('min_price'),
            'max_price': request.query_params.get('max_price'),
            'in_stock': request.query_params.get('in_stock')
        }

        for key, value in filters.items():
            if value:  
                self.queryset = self.filter_queryset(key, value, request)  
        
        return self.queryset

    def filter_queryset(self, key, value, request):  
        try:
            if key == 'min_price':
                min_price = int(value)
                self.queryset = self.queryset.filter(price__gte=min_price)

            if key == 'max_price':
                max_price = int(value)
                self.queryset = self.queryset.filter(price__lte=max_price)

            min_price_param = request.query_params.get('min_price')  
            max_price_param = request.query_params.get('max_price')  

            if min_price_param and max_price_param:
                min_price = int(min_price_param)
                max_price = int(max_price_param)
                self.queryset = self.queryset.filter(price__gte=min_price, price__lte=max_price)

        except ValueError:
            self.error_handler('Invalid price value provided. Price must be an integer.', status_code=400)
            return self.queryset 

        if key == 'in_stock':
            if value.lower() == 'true':
                return self.queryset.filter(stock__gt=0)
            else:
                self.error_handler('Invalid value for in_stock. Must be "true" or "false".', status_code=400)
                return self.queryset  

        else:
            try:
                return self.queryset.filter(**{f"{key}__slug" if key == 'category' else key: value})
            except Exception as e:
                self.error_handler(f'Error applying filter for {key}: {str(e)}', status_code=400)
                return self.queryset 


class ProductSearch:
    @staticmethod
    def get_text_similarity(text1, text2):
        """محاسبه شباهت متنی ساده"""
        text1 = re.sub(r'[^\w\s]', '', text1.lower())
        text2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0

    @staticmethod
    def search_products(queryset, search_query):
        if search_query:
            products = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            ).distinct()

            results = []
            for product in products:
                product_text = f"{product.title} {product.description}"
                similarity = ProductSearch.get_text_similarity(search_query, product_text)

                if search_query.lower() in product.title.lower():
                    similarity += 0.3

                results.append({
                    'id': product.id,
                    'title': product.title,
                    'description': product.description,
                    'category': product.category.name,
                    'similarity': round(similarity, 3)
                })

            results.sort(key=lambda x: x['similarity'], reverse=True)
            return {'lk': results}  

        return {'lk': []}
    
class ProductListAPIView(APIView):
    pagination_class = CustomPageNumberPagination

    def get_view_count_queryset(self):
        queryset = Product.objects.all()
        view_count_subquery = MostViewed.objects.filter(product=OuterRef('pk')) \
            .values('product') \
            .annotate(count=Count('id')) \
            .values('count')
        return queryset.annotate(view_count_annotation=Subquery(view_count_subquery))

    def get_queryset(self, request):
        queryset = self.get_view_count_queryset()
        search_query = request.query_params.get('search')
        
        product_queryset = ProductQuerySet(queryset, self.handle_error)
        product_queryset.apply_search(search_query)
        product_queryset.apply_filters(request)

        ordering = self.get_ordering(request)
        return product_queryset.queryset.order_by(ordering) if not isinstance(ordering, Response) else ordering

    def get_ordering(self, request):
        ordering = request.query_params.get('ordering', '-view_count_annotation') 
        ordering_options = {
            'newest': '-created',  
            'best_selling': '-sold',  
            'cheapest': 'price', 
            'most_expensive': '-price'  
        }
        
        page = request.query_params.get('page')
        if page == 'store':
            if ordering in ordering_options:
                return ordering_options[ordering]  
            else:
                return self.handle_error(f"Invalid ordering option: {ordering}", status=status.HTTP_400_BAD_REQUEST) 

        return ordering

    def get(self, request):
        paginator = self.pagination_class()
        
        try:
            queryset = self.get_queryset(request)  
            page = paginator.paginate_queryset(queryset, request)
            
            serializer = ProductSerializer(page, many=True)
            
            return paginator.get_paginated_response(serializer.data)

        except DatabaseError as db_error:
            return self.handle_error('Database error occurred: ' + str(db_error), status.HTTP_500_INTERNAL_SERVER_ERROR)
        except NotFound as nf_error:
            return self.handle_error('Requested resource not found: ' + str(nf_error), status.HTTP_404_NOT_FOUND)
        except ValidationError as val_error:
            return self.handle_error('Validation error occurred: ' + str(val_error), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return self.handle_error('An unexpected error occurred: ' + str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_error(self, message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
        return Response({'error': message}, status=status_code) 



class ProductDetailAPIView(APIView):
    """
    API view to retrieve details of a specific product.
    """

    def get_object(self, slug):
        """
        Retrieve a product by its slug, prefetching related galleries and selecting the category.
        """
        return get_object_or_404(
            Product.objects.prefetch_related('productgallery_set').select_related('category'),
            slug=slug
        )

    def get(self, request, slug):
        """
        Handle GET requests to retrieve product details.
        """
        try:
            product = self.get_object(slug)
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return self.handle_error(f'An unexpected error occurred: {str(e)}')

    def handle_error(self, message):
        """
        Centralized error handling method.
        """
        return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# search vectore
# class ProductSearchView(APIView):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.serializer_class = ProductSearchSerializer

#     def get_text_similarity(self, text1, text2):
#         """محاسبه شباهت متنی ساده"""
#         text1 = re.sub(r'[^\w\s]', '', text1.lower())
#         text2 = re.sub(r'[^\w\s]', '', text2.lower())
        
#         words1 = set(text1.split())
#         words2 = set(text2.split())
        
#         intersection = len(words1.intersection(words2))
#         union = len(words1.union(words2))
        
#         if union == 0:
#             return 0
#         return intersection / union

#     def post(self, request):
#         query = request.data.get('query', '').strip()
#         top_k = min(int(request.data.get('top_k', 10)), 100)
#         category_id = request.data.get('category_id')

#         if not query:
#             return Response({
#                 'error': 'جستجو نمی‌تواند خالی باشد'
#             }, status=400)

#         base_queryset = Product.objects.all()
#         if category_id:
#             base_queryset = base_queryset.filter(category_id=category_id)

#         products = base_queryset.filter(
#             Q(title__icontains=query) |
#             Q(description__icontains=query)
#         ).distinct()

#         if not products.exists():
#             return Response([])

#         results = []
#         for product in products:
#             product_text = f"{product.title} {product.description}"
            
#             similarity = self.get_text_similarity(query, product_text)
            
#             if query.lower() in product.title.lower():
#                 similarity += 0.3
            
#             results.append({
#                 'id': product.id,
#                 'title': product.title,
#                 'description': product.description,
#                 'category': product.category.name,
#                 'similarity': round(similarity, 3)
#             })

#         results.sort(key=lambda x: x['similarity'], reverse=True)
#         results = results[:top_k]

#         return Response(results)
