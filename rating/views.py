from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from .serializers import RatingSerializer
from .models import Rating

from products.models import Product

# Create your views here.


class RatingListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # دریافت همه امتیازات کاربر
        ratings = Rating.objects.filter(user=request.user)
        serializer = RatingSerializer(
            ratings, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = RatingSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RatingDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Rating, pk=pk, user=user)

    # def get(self, request, pk):
    #     rating = self.get_object(pk, request.user)
    #     serializer = RatingSerializer(rating, context={'request': request})
    #     return Response(serializer.data)

    def put(self, request, pk):
        rating = self.get_object(pk, request.user)
        serializer = RatingSerializer(
            rating, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk):
    #     rating = self.get_object(pk, request.user)
    #     rating.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
