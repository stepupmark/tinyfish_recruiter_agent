from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from core.utlis import error_response,success_response,CustomPageNumberPagination
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import (
        Recruiter,
        JobPosting,
        JobApplication,
        InterviewSchedule
    )
from .validators import (
        RecruiterJobPostValidator,
    )
from .serializers import (
        JobPostingSerializer,
    )

# Create your views here.
class RecruiterJobPostAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def post(self,request):
        try:
            user = request.user
            print("USER ID",user.recruiter)
            validator = RecruiterJobPostValidator(data=request.data)
            if not validator.is_valid():
                return Response(error_response(message="validation error",errors=validator.errors),status=status.HTTP_400_BAD_REQUEST)
            validated_data = validator.validated_data

            job_posting_obj = JobPosting.objects.create(**validated_data,recruiter_id=user.recruiter.id)
            return Response(success_response(message="Job Post Created Successfully",data={}),status=status.HTTP_201_CREATED)
            

        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_400_BAD_REQUEST)
        
    def get(self,request):
        try:
            user = request.user
            job_posts = JobPosting.objects.filter(recruiter=user.recruiter).select_related('recruiter','recruiter__user').order_by('-created_at')
            paginator = self.pagination_class()
            paginated_qs = paginator.paginate_queryset(job_posts,request)
            serializer = JobPostingSerializer(paginated_qs,many=True,context={"request":request})
            paginated_response = paginator.get_paginated_response(serializer.data)

            return Response(success_response(message="Recruiter Job Posts",data=paginated_response.data),status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_400_BAD_REQUEST)

        

