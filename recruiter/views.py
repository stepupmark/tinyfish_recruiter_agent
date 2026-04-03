from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from core.utlis import error_response,success_response,CustomPageNumberPagination
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsRecruiter
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
        RecruiterJobApplicationSerializer,
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
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self,request):
        try:
            user = request.user
            job_posts = JobPosting.objects.filter(recruiter=user.recruiter,is_active=True).select_related('recruiter','recruiter__user').order_by('-created_at')
            paginator = self.pagination_class()
            paginated_qs = paginator.paginate_queryset(job_posts,request)
            serializer = JobPostingSerializer(paginated_qs,many=True,context={"request":request})
            paginated_response = paginator.get_paginated_response(serializer.data)

            return Response(success_response(message="Recruiter Job Posts",data=paginated_response.data),status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class  RecruiterJobPostDetailAPIView(APIView):
    authentication_classes = []
    permission_classes =[]

    def get(self,request,id):
        try:
            user = request.user
            job_post = JobPosting.objects.filter(id=id,is_active=True).first()
            if not job_post:
                return Response(error_response(message="Job Post Not Found",errors="No Job Post Found"),status=status.HTTP_404_NOT_FOUND)

            serialier = JobPostingSerializer(job_post,context={"request":request})

            return Response(success_response(message="Recruiter Job Post Detail",data=serialier.data),status=status.HTTP_200_OK)


        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def put(self,request,id):
        try:
            job_post_detail = JobPosting.objects.filter(id=id).first()
            if not job_post_detail:
                return Response(error_response(message="Job Post Not Found",errors="No Job Post Found"),status=status.HTTP_404_NOT_FOUND)
            validator = RecruiterJobPostValidator(data=request.data,partial=True)
            if not validator.is_valid():
                return Response(error_response(message="Validation Failed",errors=validator.errors),status=status.HTTP_400_BAD_REQUEST)
            validated_data = validator.validated_data
            for field, value in validated_data.items():
                setattr(job_post_detail,field,value)
            job_post_detail.save()
            # Updated Data
            serializer = JobPostingSerializer(job_post_detail,context={"request":request})
            return Response(success_response(message="Job Post Updated Successfully",data=serializer.data),status=status.HTTP_200_OK)

        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def delete(self,request,id):
        try:
            job_post_detail = JobPosting.objects.filter(id=id,is_active=True).first()
            if not job_post_detail:
                return Response(error_response(message="Job Post Not Found",errors="No Job Post Found"),status=status.HTTP_404_NOT_FOUND)
            
            job_post_detail.is_active=False
            job_post_detail.save()
            return Response(success_response(message="Job Post Deleted Successfully",data={}),status=status.HTTP_200_OK)

        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class RecruiterJobApplicationsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsRecruiter]
    pagination_class = CustomPageNumberPagination

    def get(self,request,job_id):
        try:
            user = request.user
            recruiter = getattr(user,"recruiter",None)
            if recruiter is None:
                return Response(error_response(message="Permission denied", errors="User is not a recruiter"),status=status.HTTP_403_FORBIDDEN)
            job_applications = JobApplication.objects.filter(job__id = job_id,
                                                             job__recruiter = user.recruiter,
                                                             is_active = True).select_related('job','user','user__candidate_profile')
            if not job_applications.exists():
                return Response(success_response(message="No Job Applications Found",data={}),status=status.HTTP_200_OK)
            
            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(job_applications,request)
            serializer = RecruiterJobApplicationSerializer(paginated_data,many=True,context={"request":request})
            paginated_response = paginator.get_paginated_response(serializer.data)

            return Response(success_response(message="Candidate Job Applications",data=paginated_response.data),status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)