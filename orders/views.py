from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Order, OrderStatusManager , Address
from .serializers import (
    OrderSerializer, OrderCreateSerializer , AddressSerializer
)
# Create your views here.

class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            order = serializer.save()

            # Add cart items to the order
            cart_items = request.user.cart.items.all()
            order.cart_items.set(cart_items)

            return Response({
                'message': 'Order successfully registered',
                'order_number': order.order_number
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(
            user=request.user
        ).prefetch_related(
            'cart_items',
            'status_logs',
            'cart_items__product'
        )
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(
            Order.objects.prefetch_related(
                'cart_items',
                'status_logs',
                'cart_items__product'
            ),
            pk=pk,
            user=user
        )

    def get(self, request, pk):
        order = self.get_object(pk, request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        order = self.get_object(pk, request.user)
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        order = self.get_object(pk, request.user)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        try:
            order_manager = OrderStatusManager(order)
            order_manager.cancel()
            return Response({'status': 'Order cancelled'})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class OrderProcessPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        selected_bank = request.data.get('bank_type')

        if not selected_bank:
            return Response(
                {'error': 'Bank type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order_manager = OrderStatusManager(order)
            order_manager.process_payment(selected_bank)
            return Response({'status': 'Payment processed'})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )




class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Address.objects.get(pk=pk, user=self.request.user)
        except Address.DoesNotExist:
            return None

    def get(self, request, pk):
        address = self.get_object(pk)
        if address is None:
            return Response({'error': 'آدرسی یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    # def put(self, request, pk):
    #     address = self.get_object(pk)
    #     if address is None:
    #         return Response({'error': 'آدرسی یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)
    #     serializer = AddressSerializer(address, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk):
    #     address = self.get_object(pk)
    #     if address is None:
    #         return Response({'error': 'آدرسی یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)
    #     address.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)