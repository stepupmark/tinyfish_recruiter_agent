from rest_framework import serializers
from recruiter.models import (
        JobPosting,
        JobApplication
    )


class JobApplicationValidator(serializers.Serializer):
    job = serializers.CharField(required=True,allow_blank=False,allow_null=True,error_messages={
        'required':'Job Post is Required',
        'null':'Job Post cannot be null',
        'blank':'Job Post cannot be Blank',
    })

    resume = serializers.FileField(required=True,allow_null=True,error_messages={
        'required':'Resume is Required',
        'null':'Resume cannot be null',
    })


    def validate(self,data):
        request = self.context.get("request")
        job_id =  data.get('job')
        user = request.user

        if not JobPosting.objects.filter(id=job_id).exists():
            raise serializers.ValidationError("Job Does not Exist")
        
        if JobApplication.objects.filter(job_id=job_id, user=user).exists():
            raise serializers.ValidationError({"job":"You have already applied for this job"})
        return data

class InterviewScheduleValidator(serializers.Serializer):
    job = serializers.CharField(required=True,allow_blank=False,allow_null=True,error_messages={
        'required':'Job Post is Required',
        'null':'Job Post cannot be null',
        'blank':'Job Post cannot be Blank',
    })