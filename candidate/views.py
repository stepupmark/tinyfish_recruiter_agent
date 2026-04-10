from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
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
        ScheduledInterviewsSerializer,
    )
from .validators import (
        JobApplicationValidator,
        InterviewScheduleValidator,
        InterviewProcessValidator,
        AnswerEvaluationValidator,
        
    )
from .services.n8n_service import (
        candidate_resume_analysis,
        candidate_schedule_interview_workflow,
    )
from .services.interview_module import (
        interview_resume_analysis,
        start_interview_process,
        evaluate_interview_answer,
    )
from recruiter.serializers import (
    RecruiterProfileSerializer
)
from authentication.models import (
    CustomUserModel,
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
            job_suggestions = JobPosting.objects.filter(is_active=True,status=UserStatusChoices.ACTIVE)

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
                        message=f"Interview has not started yet. {hours} hours {minutes} minutes remaining.",
                        errors=f"{hours} hours {minutes} minutes remaining"
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif interview_datetime <= current_time <= grace_time:

                interview_module= interview_resume_analysis(resume)

                if not interview_module["success"]:
                    return Response(error_response(message="Interview service failed",errors=interview_module["error"]),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Updating the session id from interview process

                data = interview_module.get("data", {})


                interview_schedule.interview_session_id = data.get("session_id")

                interview_schedule.save()


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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def post(self,request):
        try:
            user = request.user
            print(user.id)
            validator =  InterviewScheduleValidator(data=request.data,context={"request":request})
            if not validator.is_valid():
                return Response(error_response(message="Validation Error",errors=validator.errors),status=status.HTTP_400_BAD_REQUEST)
            
            validated_data =validator.validated_data

            if InterviewSchedule.objects.filter(application=validated_data['job_application']).exists():
                return Response(error_response(message="Already Interview Scheduled",errors="interview already scheduled"),status=status.HTTP_400_BAD_REQUEST)
            
            job_application = JobApplication.objects.filter(id=validated_data['job_application']).first()
            if not job_application:
                return Response(error_response(message="Invalid Job Application Id",errors="invalid job application"),status=status.HTTP_400_BAD_REQUEST)
            elif job_application.application_status==ApplicationStatus.REJECTED:
                return Response(error_response(message="Interview scheduling is not available as your application was not selected.",errors="Application rejected"),status=status.HTTP_403_FORBIDDEN)
            
            resume_file = job_application.resume
            interview_datetime = datetime.combine(validated_data['interview_date'],validated_data['interview_time']).strftime("%Y-%m-%d %H:%M")

            candidate_schedule_interview = candidate_schedule_interview_workflow(resume_file,interview_datetime,str(job_application.id))
            candidate_interview_data = candidate_schedule_interview.get("data",{})
            
            with transaction.atomic():
                schedule_interview = InterviewSchedule.objects.create(application_id=job_application.id,
                                                                    job_id=job_application.job.id,
                                                                    candidate=user,
                                                                    interview_date=validated_data['interview_date'],
                                                                    interview_time=validated_data['interview_time'],
                                                                    interview_link = candidate_interview_data.get("interview_link"),
                                                                    )
                job_application.application_status=ApplicationStatus.INTERVIEW_SCHEDULED
                job_application.save()


            return Response(success_response(message="Already Interview Scheduled",data={"id":schedule_interview.id,"interview_link":candidate_interview_data.get("interview_link")}),status=status.HTTP_200_OK)
            
            

        except Exception as e:
            return Response(error_response(message="Something went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    

    def get(self,request):
        try:

            user =request.user
            scheduled_interviews = InterviewSchedule.objects.filter(candidate=user)

            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(scheduled_interviews,request)
            serializer = ScheduledInterviewsSerializer(paginated_data,many=True,context={"request":request})
            paginated_response = paginator.get_paginated_response(serializer.data)

            return Response(success_response(message="Scheduled Interviews List",data=paginated_response.data),status=status.HTTP_200_OK)

            

        except Exception as e:
            return Response(error_response(message="Something went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CandidateInterviewProcessBeginAPIView(APIView):
    authentication_classes =[]
    permission_classes = []

    def post(self,request):
        try:
            validator =InterviewProcessValidator(data=request.data)
            
            if not validator.is_valid():
                return Response(error_response(message="Validation Error",errors=validator.errors),status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = validator.validated_data

            session_id = validated_data.get('session_id')
            candidate_role = validated_data.get('candidate_role')


            interview_process = start_interview_process(session_id,candidate_role)

            if not interview_process['success']:
                return Response(error_response(message="Interview Service Failed",errors=interview_process['error']),status=status.HTTP_400_BAD_REQUEST)
            
            question_data = interview_process['data']['question']

            return Response(success_response(message="Interview Process Begins",data={
                                                                "total_questions":interview_process['data']['total_questions'],
                                                                "question_no":1,
                                                                "question":question_data['question'],
                                                                "difficulty_level":question_data['difficulty'],
                                                                # "interview_process":interview_process,
                                                            }),status=status.HTTP_200_OK)


        
        except Exception as e:
            return Response(error_response(message="Something went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnswerEvaluationAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self,request):
        try:
            validator = AnswerEvaluationValidator(data=request.data)
            if not validator.is_valid():
                return Response(error_response(message="Validation Error",errors=validator.errors),status=status.HTTP_400_BAD_REQUEST)
            validated_data = validator.validated_data

            session_id = validated_data.get("session_id")
            answer = validated_data.get("answer")

            evaluate_answer = evaluate_interview_answer(session_id,answer)

            if not evaluate_answer['success']:
                return Response(error_response(message="Interview Service Failed",errors=evaluate_answer['error']),status=status.HTTP_400_BAD_REQUEST)
            
            data = evaluate_answer.get('data', {})

            scorecard =  data.get('scorecard')
            overall_score = scorecard.get('overall_score') if scorecard else None

            if scorecard:
                interview_schedule = InterviewSchedule.objects.filter(interview_session_id=session_id).first()
                interview_schedule.scored_card=overall_score
                interview_schedule.clarity=scorecard.get('comm_metrics').get('clarity')
                interview_schedule.confidence=scorecard.get('comm_metrics').get('confidence')
                interview_schedule.interview_status = InterviewStatus.COMPLETED
                interview_schedule.save()

                # Updated Job Application to interview Completed
                job_application = JobApplication.objects.filter(id=interview_schedule.application.id).first()
                job_application.application_status=ApplicationStatus.INTERVIEW_COMPLETED
                job_application.save()


            return Response(success_response(message="Interview Process",data={
                                                                # "response":evaluate_answer,
                                                                "question_no":data.get('current_index'),
                                                                "total_questions":data.get('total_questions'),
                                                                "next_question": data.get('next_question'),
                                                                "scorecard": data.get('scorecard'),

                                                                }),status=status.HTTP_200_OK)

        except Exception as e:
            return Response(error_response(message="Something went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class CandidateDashboardAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user =request.user
            print(user.full_name)
            candidate_cards= {}

            # Candidate Side
            job_applications = JobApplication.objects.filter(user=user)
            shortlisted_applications_count = job_applications.filter(application_status__in=[ApplicationStatus.SHORTLISTED,ApplicationStatus.INTERVIEW_SCHEDULED]).count()
            rejected_applications_count = job_applications.filter(application_status=ApplicationStatus.SHORTLISTED).count()
            scheduled_interviews = job_applications.filter(application_status=ApplicationStatus.INTERVIEW_SCHEDULED).count()
            total_applications = job_applications.filter(user=user).count()

            candidate_cards['total_applications']=total_applications
            candidate_cards['shortlisted_applications_count']=shortlisted_applications_count
            candidate_cards['rejected_applications_count']=rejected_applications_count
            candidate_cards['scheduled_interviews']=scheduled_interviews

            return Response(success_response(message="Candidate Dashboard Cards.",data=candidate_cards),status=status.HTTP_200_OK)

        except Exception as e:
            return Response(error_response(message="Something went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CandidateProfileAPIView(APIView):
    authentication_classes =[JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user = request.user

            candidate_profile = CustomUserModel.objects.filter(id=user.id).first()
            if not  candidate_profile:
                return Response(error_response(message="No Candidate Profile Found",errors="no profile found"),status=status.HTTP_400_BAD_REQUEST)
            serializer = RecruiterProfileSerializer(candidate_profile,context={"request":request})

            return  Response(success_response(message="Candidate Profile",data=serializer.data),status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
