from rest_framework import serializers



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