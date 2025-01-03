import logging

from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError
from rest_framework import status

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Payment ,Order, OrderStatusManager , Address
from . import serializers

# Create your views here.
logger = logging.getLogger(__name__)

# Order
class OrderCreateAPIView(APIView):
    """
    API View for creating and displaying user order.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves the list of user orders and addresses.
        """
        try:
            orders = Order.objects.filter(
                user=request.user,status='PENDING'
            ).prefetch_related('addresses','status_logs')
            print(orders.exists())
            if not orders.exists():
                return Response(
                    {"error": "No pending orders found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            addresses = Address.objects.filter(user=request.user)
            serializer_orders = serializers.OrderCreateSerializer(orders, many=True)
            serializer_addresses = serializers.AddressSerializer(addresses, many=True)
            return Response({
                'order': serializer_orders.data,
                'addresses': serializer_addresses.data
            })
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            return Response(
                {"error": "Failed to retrieve orders. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Creates a new order.
        """
        try:
            if not request.data.get('status'):
                return Response(
                    {"error": "Order status is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Order.objects.filter(user=request.user, status='PENDING').exists():
                Order.objects.filter(user=request.user, status='PENDING').delete()
            serializer = serializers.OrderCreateSerializer(
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError as e:
            logger.error(f"Error creating order: {str(e)}")
            return Response(
                {"error": "Invalid data. Please check your information."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except TypeError as e:
            logger.error(f"Error creating order: {str(e)}")
            return Response(
                {"error": "Invalid data type. Please check your information."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return Response(
                {"error": "Failed to create order. Please check your information."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Payment
class PaymentAPIView(APIView):
    """
    API View for processing payment.

    Request Body:
    {
        "bank_type": "...",  # Required
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Processes payment for the pending order of the authenticated user.
        """
        try:
            order = Order.objects.get(user=request.user, status='pending')
        except Order.DoesNotExist:
            return Response(
                {'error': 'No pending order found'},
                status=status.HTTP_404_NOT_FOUND
            )

        selected_bank = request.data.get('bank_type')

        if not selected_bank:
            return Response(
                {'error': 'Bank type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order_manager = OrderStatusManager(order)
            order_manager.process_payment(selected_bank)
            payment = Payment.objects.create(
                bank_record=order_manager.bank_record,
                order=order,
                tracking_code=order_manager.tracking_code,
                amount=order_manager.amount,
                status=order_manager.status
            )
            serializer = serializers.PaymentSerializer(payment)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except TypeError as e:
            return Response(
                {'error': 'Invalid data type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ConnectionError as e:
            return Response(
                {'error': 'Failed to connect to database'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except TimeoutError as e:
            return Response(
                {'error': 'Request timed out'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Address
class AddressCreateView(APIView):
    """
    API View for creating a new address.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Creates a new address.
        
        Request Body:
        {
            "street_address": "...",
            "city": "...",
            "state": "...",
            "postal_code": "..."
        }
        """
        try:
            serializer = serializers.AddressSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user) 
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as e:
            logger.error(f"Validation error while creating address: {str(e)}")
            return Response(
                {"error": "Invalid data provided. Please check your input."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except TypeError as e:
            logger.error(f"Type error while creating address: {str(e)}")
            return Response(
                {"error": "Invalid data type. Please check your input."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ConnectionError as e:
            logger.error(f"Connection error while creating address: {str(e)}")
            return Response(
                {"error": "Failed to connect to database. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except TimeoutError as e:
            logger.error(f"Timeout error while creating address: {str(e)}")
            return Response(
                {"error": "Request timed out. Please try again later."},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except DatabaseError as e:
            logger.error(f"Database error while creating address: {str(e)}")
            return Response(
                {"error": "Failed to create address due to database error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except IntegrityError as e:
            logger.error(f"Integrity error while creating address: {str(e)}")
            return Response(
                {"error": "Failed to create address due to integrity error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error creating address: {str(e)}")
            return Response(
                {"error": "Failed to create address. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AddressDetailView(APIView):
    """
    API View for updating and deleting an address.
    """
    permission_classes = [IsAuthenticated]
    
    def get_address(self, pk, user):
        """
        Helper method to get an address by ID and ensure it belongs to the user.
        """
        try:
            address = Address.objects.get(pk=pk, user=user)
            return address
        except Address.DoesNotExist:
            logger.error(f"Address not found or does not belong to the user. Address ID: {pk}, User: {user.id}")
            return None

    def put(self, request, pk):
        """
        Updates an address.
        
        Request Body:
        {
            "street_address": "...",
            "city": "...",
            "state": "...",
            "postal_code": "..."
        }
        """
        try:
            address = Address.objects.get(pk=pk)
            if not address:
                return Response(
                    {"error": "Address not found or you do not have permission to edit it."},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = serializers.AddressSerializer(address, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as e:
            logger.error(f"Validation error while updating address: {str(e)}")
            return Response(
                {"error": "Invalid data provided. Please check your input."},
                status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as e:
            logger.error(f"Database error while updating address: {str(e)}")
            return Response(
                {"error": "Failed to update address due to database error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except IntegrityError as e:
            logger.error(f"Integrity error while updating address: {str(e)}")
            return Response(
                {"error": "Failed to update address due to integrity error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error while updating address: {str(e)}", exc_info=True)
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def delete(self, request, pk):
        """
        Deletes an address.
        """
        try:
            address = self.get_address(pk, request.user)
            if not address:
                return Response(
                    {"error": "Address not found or you do not have permission to delete it."},
                    status=status.HTTP_403_FORBIDDEN
                )

            address.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DatabaseError as e:
            logger.error(f"Database error while deleting address: {str(e)}")
            return Response(
                {"error": "Failed to delete address due to database error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error while deleting address: {str(e)}", exc_info=True)
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
