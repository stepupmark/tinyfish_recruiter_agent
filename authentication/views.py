from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.general import SerializerError
from django.db import transaction
from rest_framework import serializers
from authentication.models import(
                CustomUserModel

            )
from recruiter.models import (
                Recruiter,

)
from candidate.models import (
                CandidateProfile,

)

from core.utlis import (
                CustomPageNumberPagination,
                success_response,
                error_response,
                
            )
from .validators import (
                RecruiterRegisterationValidator,
                CandidateRegistrationValidator,

            )

# Create your views here.

class RecruiterRegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self,request):
        try:
            validator = RecruiterRegisterationValidator(data=request.data)
            if not validator.is_valid():
                return Response(error_response(message="validation error",errors=validator.errors),status=status.HTTP_400_BAD_REQUEST)
                
            validated_data = validator.validated_data
            with transaction.atomic():
                customer_user = CustomUserModel.objects.create(
                                full_name=validated_data.get('full_name'),
                                username=validated_data.get('email'),
                                email = validated_data.get('email'),
                                mobile = validated_data.get('mobile'),
                                role = validated_data.get('role'),
                            )
                customer_user.set_password(validated_data.get('password'))
                customer_user.save()

                recruiter = Recruiter.objects.create(
                    user_id=customer_user.id,
                    company_name=validated_data.get('company_name'),
                    company_email=validated_data.get('email'),
                    gst_number=validated_data.get('gst_number'),
                    pan_number=validated_data.get('pan_number'),
                    company_registration_number=validated_data.get('company_registration_number'),
                    address=validated_data.get('address'),
                    city=validated_data.get('city'),
                    state=validated_data.get('state'),
                    country=validated_data.get('country'),
                    pincode=validated_data.get('pincode'),
                    company_website=validated_data.get('company_website'),
                    company_size=validated_data.get('company_size'),
                    industry=validated_data.get('industry'),
                    company_description=validated_data.get('company_description'),

                )
   
                
            return Response(success_response(message="Registeration Successfully",data={"user_id":customer_user.id}),status=status.HTTP_200_OK)

        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_400_BAD_REQUEST)
        

class CandidateRegisterAPIView(APIView):
    authentication_classes =[]
    permission_classes =[]
    
    def post(self,request):
        try:
            validator = CandidateRegistrationValidator(data=request.data)
            if not validator.is_valid():
                return Response(error_response(message="validation error",errors=validator.errors),status=status.HTTP_400_BAD_REQUEST)
            validated_data = validator.validated_data
            with transaction.atomic():
                customer_user = CustomUserModel.objects.create(
                                full_name=validated_data.get('full_name'),
                                username=validated_data.get('email'),
                                email = validated_data.get('email'),
                                mobile = validated_data.get('mobile'),
                                role = validated_data.get('role'),
                            )
                customer_user.set_password(validated_data.get('password'))
                customer_user.save()

                candidate = CandidateProfile.objects.create(
                    user_id=customer_user.id,
                    location=validated_data.get('location'),
                    current_job_title=validated_data.get('current_job_title'),
                    total_experience=validated_data.get('total_experience'),
                    profile_photo=validated_data.get('profile_photo'),
                )

                return Response(success_response(message="Candidate registered successfully",data={"user_id":customer_user.id}),status=status.HTTP_201_CREATED)


        except Exception as e:
            return Response(error_response(message="Something went wrong",errors=str(e)),status=status.HTTP_400_BAD_REQUEST)

    