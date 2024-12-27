from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import DatabaseError

from .models import Promotion
from .serializers import PromotionSerializer
from .permissions import IsPromotionAdmin
# Create your views here.

# get Promotion listings
class PromotionListView(APIView):
    """
    PromotionListView handles the retrieval of promotion(coupon & discount product) listings.
    """
    permission_classes = [IsPromotionAdmin]

    def get(self, request):
        """
        Handles GET requests to retrieve promotions.
        """
        try:
            promotions = Promotion.objects.all()

            is_active = request.query_params.get('is_active')
            if is_active is not None:
                if is_active.lower() not in ['true', 'false']:
                    return Response({'error': 'Invalid value for is_active. Must be "true" or "false".'},
                                    status=status.HTTP_400_BAD_REQUEST)
                promotions = promotions.filter(is_active=is_active.lower() == 'true')

            start_date = request.query_params.get('start_date')
            if start_date:
                try:
                    start_date = timezone.datetime.fromisoformat(start_date)
                    promotions = promotions.filter(start_date__gte=start_date)
                except ValueError:
                    return Response({'error': 'Invalid start_date format. Use YYYY-MM-DD.'},
                                    status=status.HTTP_400_BAD_REQUEST)
            end_date = request.query_params.get('end_date')
            if end_date:
                try:
                    end_date = timezone.datetime.fromisoformat(end_date)
                    promotions = promotions.filter(end_date__lte=end_date)
                except ValueError:
                    return Response({'error': 'Invalid end_date format. Use YYYY-MM-DD.'},
                                    status=status.HTTP_400_BAD_REQUEST)

            discount_type = request.query_params.get('discount_type')
            if discount_type:
                if discount_type not in dict(Promotion.PROMOTION_TYPES).keys():
                    return Response({'error': 'Invalid discount_type. Must be one of: PRODUCT, COUPON.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                promotions = promotions.filter(discount_type=discount_type)

            serializer = PromotionSerializer(promotions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except DatabaseError as db_error:
            return Response({'error': 'Database error occurred: ' + str(db_error)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred: ' + str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class PromotionDetailView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, pk):
#         promotion = get_object_or_404(Promotion, pk=pk)
#         serializer = PromotionSerializer(promotion)
#         return Response(serializer.data)

# get Cart list products
# class CartItemListView(APIView):
#     permission_classes = [IsCartOwner]

#     def get(self, request):
#         cart_items = CartItem.objects.filter(user=request.user, is_active=True)
#         serializer = CartItemSerializer(cart_items, many=True)
#         totals = calculate_cart_totals(cart_items)
#         return Response({
#             'items': serializer.data,
#             'totals': totals
#         })

#     def post(self, request):
#         serializer = CartItemSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CartItemDetailView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, pk):
#         cart_item = get_object_or_404(
#             CartItem, pk=pk, user=request.user
#         )
#         serializer = CartItemSerializer(cart_item)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         cart_item = get_object_or_404(
#             CartItem, pk=pk, user=request.user
#         )
#         serializer = CartItemSerializer(cart_item, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         cart_item = get_object_or_404(
#             CartItem, pk=pk, user=request.user
#         )
#         cart_item.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# Coupon
class CouponView(APIView):
    """
    CouponView handles the validation of discount codes (coupons).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Validate the provided coupon code.
        Request Body:
        {
            "code": "COUPON code",
        }
        """
        coupon_code = request.data.get('code')

        if not coupon_code:
            return Response({"error": "Code is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            promotion = get_object_or_404(
                Promotion,
                code=coupon_code,
                discount_type='COUPON',
                is_active=True
            )

            if not promotion.is_valid():
                return Response(
                    {"error": "Discount code is not valid or has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = PromotionSerializer(promotion)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except DatabaseError as db_error:
            return Response(
                {"error": "Database error occurred: " + str(db_error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
