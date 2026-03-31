from rest_framework import serializers
from .models import (
        CandidateProfile,
    )

from recruiter.models import (
        JobApplication,
        JobPosting
    )


class JobSuggestionsSerializer(serializers.ModelSerializer):

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
                    'status',
                ]
        read_only_fields = ["id"]


    
class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.job_title",read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id',
            'job_title',
            'application_status'
        ]