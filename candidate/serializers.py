from rest_framework import serializers
from .models import (
        CandidateProfile,
    )
from authentication.models import (
    CustomUserModel,
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
    date_of_applied = serializers.SerializerMethodField()
    is_interview_scheduled = serializers.SerializerMethodField()
    interview_date = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = [
            'id',
            'job_title',
            'is_interview_scheduled',
            'interview_date',
            'application_status',
            'date_of_applied'
        ]

    def get_date_of_applied(self, obj):
        if obj.created_at:
            return obj.created_at.strftime("%d %B %Y")
        return None

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
    


class ScheduledInterviewsSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source="candidate.full_name")
    job_title = serializers.CharField(source="job.job_title")
    interview_date = serializers.DateField(format="%d %b %Y")
    interview_time = serializers.TimeField(format="%I:%M %p")
    job_application = serializers.CharField(source="application.id")


    class Meta:
        model = InterviewSchedule
        fields =[
            'candidate_name',
            'job_title',
            'job_application',
            'interview_date',
            'interview_time',
            'scored_card',
            'interview_link',
            'interview_status',

        ]


class CandidateProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = CustomUserModel
        fields = [
            'full_name',
            'username',
            'email',
            'mobile',
            'profile',

        ]

    def get_profile(self,obj):
        request = self.context.get('request')
        candidate_profile = CandidateProfile.objects.filter(user=obj).first()
        if candidate_profile.profile_photo:
            return request.build_absolute_uri(candidate_profile.profile_photo.url)
        return None