from rest_framework import serializers
from datetime import date
from recruiter.models import (
        JobPosting,
        JobApplication
    )


class JobApplicationValidator(serializers.Serializer):
    job = serializers.CharField(required=True,allow_blank=False,allow_null=False,error_messages={
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
    job_application = serializers.CharField(required=True,allow_blank=False,allow_null=False,error_messages={
        'required':'Job Application is Required',
        'null':'Job Application cannot be null',
        'blank':'Job Application cannot be Blank',
    })

    interview_date = serializers.DateField(required=True,error_messages={
        'required':'Interview Date is Required',
        'invalid': 'Invalid date format (YYYY-MM-DD required)'
    })

    interview_time = serializers.TimeField(required=True,error_messages={
        'required':'Interview Time is Required',
        'invalid': 'Invalid time format (HH:MM:SS required)'
    })


    def validate_interview_date(self,value):
        if value < date.today():
            raise serializers.ValidationError("Interview date cannot be in the past")
        return value