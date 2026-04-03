from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.utlis import error_response,success_response,PageNumberPagination,CustomPageNumberPagination
from .filters import JobSuggestionsFilter
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from recruiter.models import (
        JobPosting,
        JobApplication,
        InterviewSchedule
    )
from .serializers import (
        JobSuggestionsSerializer,
        JobApplicationSerializer,
    )
from .validators import (
        JobApplicationValidator,
        InterviewScheduleValidator,
        
    )
from .services.n8n_service import (
        candidate_resume_analysis,
    )
from .services.interview_module import (
        start_interview,
    )
from core.choice_fields import (
                    EmploymentTypeChoices,
                    UserStatusChoices,
                    ApplicationStatus,
                    InterviewStatus,
                )
# Create your views here.

class CandidateJobSuggestions(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
            validator = JobApplicationValidator(data=request.data,context={'request': request})

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
            
            # Duplicate Application

            duplicate_application = JobApplication.objects.filter(job_id=validated_data["job"],user=request.user).first()
            if duplicate_application:
                return Response(error_response(message="Application already Submited",errors="application already exists"),status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():

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

                shortlist_status = n8n_response
                
                # print(shortlist_status,"Shortlist Status")

            if not n8n_response.get("success"):
                return Response(
                    error_response(
                        message=n8n_response.get("message", "N8n failed"),
                        errors=n8n_response
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )

            my_field = n8n_response.get("data", {}).get("myField")


            if my_field=="Rejected":
                print("REJECTED")
                print(job_application_obj)
                job_application_obj.application_status=ApplicationStatus.REJECTED
            else:
                print("SELECTED")
                print(job_application_obj)
                job_application_obj.application_status=ApplicationStatus.SHORTLISTED

            job_application_obj.save()

            # return Response(success_response(message="N8n Automation",data=n8n_response),status=status.HTTP_200_OK)

            serializer = JobApplicationSerializer(job_application_obj)

            return Response(
                success_response(
                    message="Job Application Submitted Successfully",
                    data={"application_id":job_application_obj.id,
                          "shortlist_status":shortlist_status,
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
        

class CandidateInterviewAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request,application_id):
        try:
            user = request.user
            interview_schedule= InterviewSchedule.objects.filter(application=application_id).first()
            if not interview_schedule:
                return Response(error_response(message="No Interview Scheduled",errors="no interview scheduled"),status=status.HTTP_400_BAD_REQUEST)
            interview_datetime = datetime.combine(
                interview_schedule.interview_date,
                interview_schedule.interview_time
            )
            

            resume = interview_schedule.application.resume
            interview_datetime = timezone.make_aware(interview_datetime)
            current_time = timezone.now()
            grace_time = interview_datetime + timedelta(minutes=5)

            if interview_datetime > current_time:
                remaining_time = interview_datetime - current_time
                total_seconds = int(remaining_time.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60

                return Response(
                    error_response(
                        message="Interview not completed",
                        errors=f"{hours} hours {minutes} minutes left"
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif interview_datetime <= current_time <= grace_time:

                interview_module= start_interview(resume)

                if not interview_module["success"]:
                    return Response(
                        error_response(
                            message="Interview service failed",
                            errors=interview_module["error"]
                        ),
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                return Response(
                    success_response(
                        message="Interview is active. You may join now.",data={"allow_interview":True,"data":interview_module}
                    ),
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    error_response(
                        message="Interview window closed",
                        errors="The interview time has expired. Please contact support if needed."
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )


        except Exception as e:
            return Response(error_response(message="Something went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class CandidateScheduleInterviewAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self,request):
        try:
            validator =  InterviewScheduleValidator(data=request.data,context={"request":request})
            

        except Exception as e:
            return Response(error_response(message="Something went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)