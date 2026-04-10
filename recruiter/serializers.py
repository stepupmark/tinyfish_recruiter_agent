from rest_framework import serializers
from datetime import datetime
from .models import (
        JobPosting,
        JobApplication,
        InterviewSchedule

    )
from authentication.models import(
    CustomUserModel
)


class JobPostingSerializer(serializers.ModelSerializer):
    recruiter = serializers.CharField(source="recruiter.user.username",read_only=True)
    company = serializers.CharField(source="recruiter.company_name",read_only=True)
    applications_count = serializers.SerializerMethodField()
    # job_description_file = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = [
                    'id',
                    'recruiter',
                    'company',
                    'job_title',
                    'job_description',
                    'job_description_file',
                    'job_location',
                    'employment_type',
                    'salary_range',
                    'skills_required',
                    'applications_count',
                    'status',
                ]
        
    def get_applications_count(self,obj):
        applications=JobApplication.objects.filter(job=obj).count()
        if applications:
            return applications
        return 0


    # def get_job_description_file(self,obj):
    #     request = self.context.get("request")
    #     if obj.job_description_file:
    #         return request.build_absolute_uri(obj.job_description_file)
    #     return None


class RecruiterJobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.job_title", read_only=True)
    candidate_resume = serializers.SerializerMethodField()
    candidate_name = serializers.CharField(source="user.full_name", read_only=True)
    candidate_mobile = serializers.CharField(source="user.mobile", read_only=True)
    candidate_location = serializers.CharField(source="user.candidate_profile.location", read_only=True)
    previous_employment = serializers.CharField(source="user.candidate_profile.current_job_title", read_only=True)
    total_experience = serializers.CharField(source="user.candidate_profile.total_experience", read_only=True)
    interview_datetime = serializers.SerializerMethodField()
    interview_status = serializers.CharField(source="job_application_interviews.interview_status")
    score_card = serializers.CharField(source="job_application_interviews.scored_card")

    class Meta:
        model = JobApplication
        fields = [
                    'id',
                    'job_title',
                    'candidate_resume',
                    'candidate_name',
                    'candidate_mobile',
                    'candidate_location',
                    'previous_employment',
                    'total_experience',
                    'application_status',
                    'interview_datetime',
                    'interview_status',
                    'score_card',

                ]
        
    def get_interview_datetime(self,obj):

        interview_schedule = getattr(obj,"job_application_interviews",None)
        if interview_schedule:
            dt= datetime.combine(interview_schedule.interview_date,interview_schedule.interview_time)
            return dt.strftime("%d %B %Y %I:%M %p")
        
        return None
        
    def get_candidate_resume(self,obj):
        request = self.context.get("request")
        if obj.resume:
            return request.build_absolute_uri(obj.resume.url)
        return None
    


class RecruiterProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUserModel
        fields = [
            'full_name',
            'username',
            'email',
            'mobile', 

        ]