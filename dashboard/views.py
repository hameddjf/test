import re

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from orders.models import Order , Address
from orders.serializers import AddressSerializer

from .serializers import UserProfileSerializer, OrderHistorySerializer

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        
        order_stats = {
            'total_orders': Order.objects.filter(user=user).count(),
            'pending_orders': Order.objects.filter(user=user, status='PENDING').count(),
            'completed_orders': Order.objects.filter(user=user, status='COMPLETED').count()
        }
        
        return Response({
            'personal_info': serializer.data,
            'order_stats': order_stats
        })

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            # اعتبارسنجی شماره تلفن
            phone_number = serializer.validated_data.get('phone_number')
            if phone_number and not re.match(r'^09\d{9}$', phone_number):
                return Response({
                    'errors': {'phone_number': 'شماره تلفن نامعتبر است'}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response({
                'message': 'اطلاعات پروفایل با موفقیت به‌روز شد',
                'user_data': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-id')
        serializer = OrderHistorySerializer(orders, many=True)
        
        return Response({
            'orders': serializer.data
        })
        
class AddressListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        
        return Response({
            'addresses': serializer.data
        })
    
    def post(self, request):
        # محدودیت تعداد آدرس‌ها
        if Address.objects.filter(user=request.user).count() >= 5:
            return Response({
                'error': 'حداکثر 5 آدرس مجاز است'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AddressSerializer(data={
            **request.data,
            'user': request.user.id
        })
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'آدرس با موفقیت اضافه شد',
                'address': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk, user):
        try:
            return Address.objects.get(pk=pk, user=user)
        except Address.DoesNotExist:
            return None
    
    def put(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response({
                'error': 'آدرس مورد نظر یافت نشد'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'آدرس با موفقیت به‌روز شد',
                'address': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response({
                'error': 'آدرس مورد نظر یافت نشد'
            }, status=status.HTTP_404_NOT_FOUND)
        
        address.delete()
        return Response({
            'message': 'آدرس با موفقیت حذف شد'
        }, status=status.HTTP_200_OK)