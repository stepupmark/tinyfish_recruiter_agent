from rest_framework import serializers



class RecruiterJobPostValidator(serializers.Serializer):
    job_title = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Job Title is Required',
        'null':'Job Title cannot be null',
        'blank':'Job Title cannot be Blank',
    })

    job_description = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Job Description is Required',
        'null':'Job Description cannot be null',
        'blank':'Job Description cannot be Blank',
    })

    job_description_file = serializers.FileField(required=True,allow_null=False,error_messages={
        'required':'Job Description File is Required',
        'null':'Job Description File cannot be null',
    
    })

    job_location = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Job Location is Required',
        'null':'Job Location cannot be null',
        'blank':'Job Location cannot be Blank',
    })

    employment_type = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Employment Type is Required',
        'null':'Employment Type cannot be null',
        'blank':'Employment Type cannot be Blank',
    })

    salary_range = serializers.CharField(required=False,allow_null=True,allow_blank=True)
    skills_required = serializers.CharField(required=False,allow_null=True,allow_blank=True)
    status = serializers.CharField(required=False,allow_null=True,allow_blank=True)

