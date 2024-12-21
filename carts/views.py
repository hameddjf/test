from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema

from .models import Promotion, CartItem
from .serializers import PromotionSerializer, CartItemSerializer
from .permissions import IsCartOwner, IsPromotionAdmin
from .utils import calculate_cart_totals, validate_promotion_code
from .validators import validate_promotion_code
# Create your views here.


@swagger_auto_schema(tags=['Promotion'])
class PromotionListView(APIView):
    permission_classes = [IsPromotionAdmin]

    def get(self, request):
        promotions = Promotion.objects.all()
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PromotionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(tags=['Promotion'])
class PromotionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        promotion = get_object_or_404(Promotion, pk=pk)
        serializer = PromotionSerializer(promotion)
        return Response(serializer.data)

    def put(self, request, pk):
        promotion = get_object_or_404(Promotion, pk=pk)
        serializer = PromotionSerializer(promotion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        promotion = get_object_or_404(Promotion, pk=pk)
        promotion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(tags=['Cart'])
class CartItemListView(APIView):
    permission_classes = [IsCartOwner]

    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        serializer = CartItemSerializer(cart_items, many=True)
        totals = calculate_cart_totals(cart_items)
        return Response({
            'items': serializer.data,
            'totals': totals
        })

    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(tags=['Cart'])
class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        cart_item = get_object_or_404(
            CartItem, pk=pk, user=request.user
        )
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    def put(self, request, pk):
        cart_item = get_object_or_404(
            CartItem, pk=pk, user=request.user
        )
        serializer = CartItemSerializer(cart_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cart_item = get_object_or_404(
            CartItem, pk=pk, user=request.user
        )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(tags=['Coupon'])
class ValidateCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        try:
            promotion = get_object_or_404(
                Promotion,
                code=code,
                discount_type='COUPON'
            )
            if promotion.is_valid():
                serializer = PromotionSerializer(promotion)
                return Response(serializer.data)
            return Response(
                {"error": "Discount code is invalid"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Promotion.DoesNotExist:
            return Response(
                {"error": "Discount code is invalid"},
                status=status.HTTP_404_NOT_FOUND
            )


@swagger_auto_schema(tags=['Coupon'])
class ApplyCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        coupon_code = request.data.get('code')
        try:
            promotion = get_object_or_404(
                Promotion,
                code=coupon_code,
                discount_type='COUPON',
                is_active=True
            )
            if not promotion.is_valid():
                return Response(
                    {"error": "Discount code is not valid"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True
            )
            cart_items.update(coupon=promotion)
            promotion.used_count += 1
            promotion.save()

            serializer = CartItemSerializer(cart_items, many=True)
            return Response(serializer.data)

        except Promotion.DoesNotExist:
            return Response(
                {"error": "Discount code is invalid"},
                status=status.HTTP_404_NOT_FOUND
            )
