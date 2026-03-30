from rest_framework import serializers
from .models import (
        JobPosting,

    )


class JobPostingSerializer(serializers.ModelSerializer):
    recruiter = serializers.CharField(source="recruiter.user.username",read_only=True)
    company = serializers.CharField(source="recruiter.company_name",read_only=True)
    job_description_file = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = ['recruiter','company','job_title','job_description','job_description_file','job_location','employment_type','salary_range','skills_required']


    def get_job_description_file(self,obj):
        request = self.context.get("request")
        if obj.job_description_file:
            return request.build_absolute_uri(obj.job_description_file)
        return None