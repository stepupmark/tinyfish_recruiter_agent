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
        RecruiterProfileSerializer,
        
    )
from candidate.services.n8n_service import(
    recruiter_jd_analysis,
)
from core.choice_fields import (
                    EmploymentTypeChoices,
                    UserStatusChoices,
                    ApplicationStatus,
                    InterviewStatus,
                )
from authentication.models import (
    CustomUserModel
)
from candidate.serializers import (
    ScheduledInterviewsSerializer,
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

            job_description_file = validated_data.get('job_description_file')
            
            # N8N Workflow to jd analysis
            jd_analysis = recruiter_jd_analysis(job_description_file)
            job_description = jd_analysis['data']['overview'] if jd_analysis else None
            skills_required = jd_analysis['data']['skills_text'] if jd_analysis else None
            job_location = jd_analysis['data']['location'] if jd_analysis else None

            job_posting_obj = JobPosting.objects.create(**validated_data,
                                                        job_description=job_description,
                                                        skills_required=skills_required,
                                                        job_location = job_location,
                                                        recruiter_id=user.recruiter.id)

            jd_analysis_data = jd_analysis.get("data",{})

            return Response(success_response(message="Job Post Created Successfully",data={
                                                                    "job_post":job_posting_obj.id,
                                                                    "jd_analysis":jd_analysis_data,
                                                                }),status=status.HTTP_201_CREATED)
            

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
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]

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
        

class RecruiterJobApplicationsListAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsRecruiter]
    pagination_class = CustomPageNumberPagination

    def get(self,request):
        try:
            user = request.user
            recruiter = getattr(user,"recruiter",None)
            if recruiter is None:
                return Response(error_response(message="Permission denied", errors="User is not a recruiter"),status=status.HTTP_403_FORBIDDEN)
            job_applications = JobApplication.objects.filter(job__recruiter = user.recruiter,
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
        


class RecruiterDashboardAPIView(APIView):
    authentication_classes =[JWTAuthentication]
    permission_classes =[IsAuthenticated]
    
    def get(self,request):
        try:
            user =request.user
            recruiter_cards= {}

            # Total Jobs Posted
            job_posts = JobPosting.objects.all()
            job_applications = JobApplication.objects.all()
            total_jobs = job_posts.filter(recruiter__user=user).count()
            active_jobs = job_posts.filter(recruiter__user=user,status=UserStatusChoices.ACTIVE,is_active=True).count()
            total_job_applications=job_applications.filter(job__recruiter__user=user).count()
            shortlisted_candidates = job_applications.filter(job__recruiter__user=user,application_status=ApplicationStatus.SHORTLISTED).count()
            rejected_candidates = job_applications.filter(job__recruiter__user=user,application_status=ApplicationStatus.REJECTED).count()
            scheduled_interviews = job_applications.filter(job__recruiter__user=user,application_status=ApplicationStatus.INTERVIEW_SCHEDULED).count()

            recruiter_cards['total_jobs']=total_jobs
            recruiter_cards['total_job_applications']=total_job_applications
            recruiter_cards['active_jobs']=active_jobs
            recruiter_cards['shortlisted_candidates']=shortlisted_candidates
            recruiter_cards['rejected_candidates']=rejected_candidates
            recruiter_cards['scheduled_interviews']=scheduled_interviews

            return Response(success_response(message="Recruiter Dashboard Cards.",data=recruiter_cards),status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class RecruiterProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user = request.user

            recruiter_profile = CustomUserModel.objects.filter(id=user.id).first()
            if not  recruiter_profile:
                return Response(error_response(message="No Recruiter Profile Found",errors="no profile found"),status=status.HTTP_400_BAD_REQUEST)
            serializer = RecruiterProfileSerializer(recruiter_profile,context={"request":request})

            return  Response(success_response(message="Recruiter Profile",data=serializer.data),status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class RecruitersJobSchdeduledInterviews(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get(self,request):
        try:
            user= request.user
            scheduled_interviews = InterviewSchedule.objects.filter(job__recruiter__user=user)

            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(scheduled_interviews,request)
            serializer = ScheduledInterviewsSerializer(paginated_data,many=True,context={"request":request})
            paginated_response = paginator.get_paginated_response(serializer.data)

            return Response(success_response(message="Scheduled Interviews List",data=paginated_response.data),status=status.HTTP_200_OK)

            
        except Exception as e:
            return Response(error_response(message="Something Went wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)