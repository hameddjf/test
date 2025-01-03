import re
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, NotFound , PermissionDenied,AuthenticationFailed

from django.db import DatabaseError
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from orders.models import Order 
from orders.views import AddressCreateView, AddressDetailView

from .serializers import UserProfileSerializer, OrderHistorySerializer
from .mixin import DashboardAddressMixin

logger = logging.getLogger(__name__)

# Profile
class ProfileView(APIView):
    """
    API View for retrieving the authenticated user's profile information.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the profile information of the authenticated user.
        """
        try:
            user = request.user
            if not user:
                logger.error("User  not found in request.")
                return Response({
                    'error': 'User  not found.'
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = UserProfileSerializer(user)
            return Response({
                'personal_info': serializer.data,
            })
        except Exception as e:
            logger.error(f"An error occurred in ProfileView: {str(e)}", exc_info=True)
            return Response({
                'error': 'An unexpected error occurred while retrieving profile information.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileUpdateView(APIView):
    """
    API View for updating the authenticated user's profile information.
    
    request body: 
    {
        "first_name": "...",
        "last_name": "...",
        "email": "...",
        "username": "...",
    }
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """
        Update the profile information of the authenticated user.
        """
        try:
            user = request.user
            if not user:
                logger.error("User  not found in request.")
                return Response({
                    'error': 'User  not found.'
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = UserProfileSerializer(user, data=request.data, partial=True)
            
            if not serializer.is_valid():
                logger.warning(f"Validation errors: {serializer.errors}")
                return Response({
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            phone_number = serializer.validated_data.get('phone_number')
            if phone_number and not re.match(r'^09\d{9}$', phone_number):
                logger.warning(f"Invalid phone number: {phone_number}")
                return Response({
                    'errors': {'phone_number': 'Invalid phone number. Phone number must start with 09 and be 11 digits long.'}
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                'message': 'Profile information updated successfully',
                'user_data': serializer.data
            })
        except Exception as e:
            logger.error(f"An error occurred in ProfileUpdateView: {str(e)}", exc_info=True)
            return Response({
                'error': 'An unexpected error occurred while updating profile information.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# OrderHistory
class OrderHistoryView(APIView):
    """
    API View for retrieving the order history of a user.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """
        Retrieves the order history of the authenticated user.
        """
        try:
            delivered_orders = Order.objects.filter(user=request.user, status='DELIVERED').select_related('user').order_by('-id', 'status')
            other_orders = Order.objects.filter(user=request.user).exclude(status='DELIVERED').select_related('user').order_by('-id', 'status')
            orders = list(delivered_orders) + list(other_orders)
            if not orders:
                logger.info(f"No orders found for user: {request.user.id}")
                return Response({
                    'message': 'No orders found.'
                })
            serializer = OrderHistorySerializer(orders, many=True)
            
            logger.info(f"Successfully fetched {len(orders)} orders for user: {request.user.id}")

            return Response({
                'orders': serializer.data
            })
        except Order.DoesNotExist:
            logger.error(f"Order not found for user {request.user.id}")
            return Response({
                'error': 'Order not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            logger.error(f"Validation error occurred for user {request.user.id}: {str(e)}")
            return Response({
                'error': 'Validation error occurred.'
            }, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            logger.error(f"Database error occurred for user {request.user.id}: {str(e)}")
            return Response({
                'error': 'Database error occurred.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"An unexpected error occurred for user {request.user.id}: {str(e)}", exc_info=True)
            return Response({
                'error': 'An unexpected error occurred.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
    def handle_exception(self, exc):
        """
        Custom exception handler for the view.
        """
        if isinstance(exc, AuthenticationFailed):
            logger.warning(f"Unauthorized access attempt: {str(exc)}")
            return Response({'error': 'User     is not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)
        elif isinstance(exc, PermissionDenied):
            logger.warning(f"Permission denied: {str(exc)}")
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        elif isinstance(exc, NotFound):
            logger.error(f"Not found: {str(exc)}")
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        elif isinstance(exc, DatabaseError):
            logger.error(f"Database error: {str(exc)}")
            return Response({'error': 'Database error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif isinstance(exc, NotFound):
            logger.error(f"Not found: {str(exc)}")
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        logger.error(f"Unexpected exception: {str(exc)}", exc_info=True)
        return super().handle_exception(exc)


class AddressCreateView(DashboardAddressMixin, AddressCreateView):
    pass

class AddressDetailView(DashboardAddressMixin, AddressDetailView):
    pass

# class AddressListView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         addresses = Address.objects.filter(user=request.user)
#         serializer = AddressSerializer(addresses, many=True)
        
#         return Response({
#             'addresses': serializer.data
#         })
    
#     def post(self, request):
#         # محدودیت تعداد آدرس‌ها
#         if Address.objects.filter(user=request.user).count() >= 5:
#             return Response({
#                 'error': 'حداکثر 5 آدرس مجاز است'
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         serializer = AddressSerializer(data={
#             **request.data,
#             'user': request.user.id
#         })
        
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 'message': 'آدرس با موفقیت اضافه شد',
#                 'address': serializer.data
#             }, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class AddressDetailView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self, pk, user):
#         try:
#             return Address.objects.get(pk=pk, user=user)
#         except Address.DoesNotExist:
#             return None
    
#     def put(self, request, pk):
#         address = self.get_object(pk, request.user)
#         if not address:
#             return Response({
#                 'error': 'آدرس مورد نظر یافت نشد'
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = AddressSerializer(address, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 'message': 'آدرس با موفقیت به‌روز شد',
#                 'address': serializer.data
#             })
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def delete(self, request, pk):
#         address = self.get_object(pk, request.user)
#         if not address:
#             return Response({
#                 'error': 'آدرس مورد نظر یافت نشد'
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         address.delete()
#         return Response({
#             'message': 'آدرس با موفقیت حذف شد'
#         }, status=status.HTTP_200_OK)