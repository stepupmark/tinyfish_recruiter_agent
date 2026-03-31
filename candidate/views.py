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

            job_application_obj = JobApplication.objects.create(
                job_id=validated_data["job"],   # don't use job_id here
                resume=validated_data["resume"],
                user=request.user
            )

            serializer = JobApplicationSerializer(job_application_obj)

            return Response(
                success_response(
                    message="Job Application Submitted Successfully",
                    data={"application_id":job_application_obj.id}
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