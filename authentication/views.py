from django.shortcuts import render
from rest_framework.views import APIView
from core.utlis import (
    CustomPageNumberPagination,
    success_response,
    error_response
    
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class UserRegisterAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    