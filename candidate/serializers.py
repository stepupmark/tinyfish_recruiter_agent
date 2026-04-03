from rest_framework import serializers
from .models import (
        CandidateProfile,
    )

from recruiter.models import (
        JobApplication,
        JobPosting,
        InterviewSchedule
    )


class JobSuggestionsSerializer(serializers.ModelSerializer):

    application_status = serializers.SerializerMethodField()

    class Meta:
        model= JobPosting
        fields = [
                    'id',
                    'job_title',
                    'job_description',
                    'job_location',
                    'employment_type',
                    'salary_range',
                    'skills_required',
                    'application_status',
                    'status',
                ]
        read_only_fields = ["id"]

    
    def get_application_status(self,obj):
        request = self.context.get("request")
        user =request.user
        print(user)
        return JobApplication.objects.filter(user=user,job=obj).exists()


    
class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.job_title",read_only=True)
    is_interview_scheduled = serializers.SerializerMethodField()
    interview_date = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = [
            'id',
            'job_title',
            'is_interview_scheduled',
            'interview_date',
            'application_status'
        ]

    def get_is_interview_scheduled(self,obj):
        return InterviewSchedule.objects.filter(application=obj.id).exists()
    
    def get_interview_date(self, obj):
        interview = InterviewSchedule.objects.filter(application=obj).first()
        if interview:
            return {
                "date": interview.interview_date,
                "time": interview.interview_time
            }
        return None