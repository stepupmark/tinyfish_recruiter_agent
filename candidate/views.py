from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.utlis import error_response,success_response,PageNumberPagination,CustomPageNumberPagination
from .filters import JobSuggestionsFilter
from recruiter.models import (
        JobPosting,
        JobApplication,
    )
from .serializers import (
        JobSuggestionsSerializer,
        JobApplicationSerializer,
    )
from .validators import (
        JobApplicationValidator,
        
    )
from candidate.services.n8n_service import (
        candidate_resume_analysis,
    )
# Create your views here.

class CandidateJobSuggestions(APIView):
    authentication_classes = []
    permission_classes = []
    pagination_class = CustomPageNumberPagination

    def get(self,request):
        try:
            job_suggestions = JobPosting.objects.filter(is_active=True)

            filterset = JobSuggestionsFilter(request.GET,queryset=job_suggestions)
            if filterset.is_valid():
                job_suggestions = filterset.qs

            paginator= self.pagination_class()
            paginated_data = paginator.paginate_queryset(job_suggestions,request)
            serializer = JobSuggestionsSerializer(paginated_data,many=True,context={"request":request})
            paginate_response = paginator.get_paginated_response(serializer.data)

            return Response(success_response(message="Candidate Job Posts Suggestions",data=paginate_response.data),status=status.HTTP_200_OK)

        except Exception as e:
            return Response(error_response(message="Something went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CandidateJobApplicationAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def post(self, request):
        try:
            validator = JobApplicationValidator(data=request.data)

            if not validator.is_valid():
                return Response(
                    error_response(
                        message="Validation Error",
                        errors=validator.errors
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )

            validated_data = validator.validated_data

            # Check Job 

            job_post = JobPosting.objects.filter(id=validated_data["job"]).first()

            if not job_post:
                return Response(error_response(message="No Job Found",errors="no job found"),status=status.HTTP_400_BAD_REQUEST)

            job_application_obj = JobApplication.objects.create(
                job_id=validated_data["job"],   # don't use job_id here
                resume=validated_data["resume"],
                user=request.user
            )

            # MAIL Automation

            # resume_file = request.FILES.get("resume")
            # job_description_file = request.FILES.get("job_description_file")
            resume_file = job_application_obj.resume
            job_description_file = job_post.job_description_file
            

            n8n_response = candidate_resume_analysis(resume_file,job_description_file)

            return Response(success_response(message="N8n Automation",data=n8n_response),status=status.HTTP_200_OK)

            serializer = JobApplicationSerializer(job_application_obj)

            return Response(
                success_response(
                    message="Job Application Submitted Successfully",
                    data={"application_id":job_application_obj.id,
                          "n8n_triggered": n8n_response["success"]}
                ),
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(error_response(message="Something went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def get(self,request):
        try:
            user = request.user
            job_applications = JobApplication.objects.filter(user=user,is_active=True)
            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(job_applications,request)
            serializer = JobApplicationSerializer(paginated_data,many=True,context={"request":request})
            paginated_response = paginator.get_paginated_response(serializer.data)

            return Response(success_response(message="Candidate Job Applications list",data=paginated_response.data),status=status.HTTP_200_OK)

        except Exception as e:
            return Response(error_response(message="Something went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)