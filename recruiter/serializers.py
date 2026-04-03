from rest_framework import serializers
from .models import (
        JobPosting,
        JobApplication,

    )


class JobPostingSerializer(serializers.ModelSerializer):
    recruiter = serializers.CharField(source="recruiter.user.username",read_only=True)
    company = serializers.CharField(source="recruiter.company_name",read_only=True)
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
                    'status',
                ]


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

                ]
        
    def get_candidate_resume(self,obj):
        request = self.context.get("request")
        if obj.resume:
            return request.build_absolute_uri(obj.resume.url)
        return None