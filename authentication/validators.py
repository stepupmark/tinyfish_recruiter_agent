from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from authentication.models import (
        CustomUserModel
)


class RecruiterRegisterationValidator(serializers.Serializer):
    full_name = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Full Name is Required',
        'null':'Full Name cannot be null',
        'blank':'Full Name cannot be Blank',
    })
    email = serializers.EmailField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Email is Required',
        'null':'Email cannot be null',
        'blank':'Email cannot be Blank',
        'invalid': 'Enter a valid email address'
    })
    password = serializers.CharField(required=True,allow_null=False,allow_blank=False,write_only=True,min_length=6,error_messages={
        'required':'Password is Required',
        'null':'Password cannot be null',
        'blank':'Password cannot be Blank',
        'min_length': 'Password must be at least 6 characters'
    })
    mobile = serializers.CharField(required=False,allow_null=True,allow_blank=True)
    role = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Role is Required',
        'null':'Role cannot be null',
        'blank':'Role cannot be Blank',
    })
    company_name = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Comapny Name is Required',
        'null':'Comapny Name cannot be null',
        'blank':'Comapny Name cannot be Blank',
    })
    gst_number = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'GST No is Required',
        'null':'GST No cannot be null',
        'blank':'GST No cannot be Blank',
    })
    pan_number = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'PAN No is Required',
        'null':'PAN No cannot be null',
        'blank':'PAN No cannot be Blank',
    })
    company_registration_number = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Registeration Number is Required',
        'null':'Registeration Number cannot be null',
        'blank':'Registeration Number cannot be Blank',
    })
    address = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Address is Required',
        'null':'Address cannot be null',
        'blank':'Address cannot be Blank',
    })
    city = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'City is Required',
        'null':'City cannot be null',
        'blank':'City cannot be Blank',
    })
    state = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'State is Required',
        'null':'State cannot be null',
        'blank':'State cannot be Blank',
    })
    country = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Country is Required',
        'null':'Country cannot be null',
        'blank':'Country cannot be Blank',
    })
    pincode = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Pincode is Required',
        'null':'Pincode cannot be null',
        'blank':'Pincode cannot be Blank',
    })
    company_website = serializers.CharField(required=False,allow_null=True,allow_blank=True)
    company_size = serializers.CharField(required=False,allow_null=True,allow_blank=True)
    industry = serializers.CharField(required=False,allow_null=True,allow_blank=True)
    company_description = serializers.CharField(required=False,allow_null=True,allow_blank=True)


    def validate_email(self, value):
        if CustomUserModel.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    
    def validate_mobile(self, value):
        if CustomUserModel.objects.filter(mobile=value).exists():
            raise serializers.ValidationError("Mobile already registered")
        return value

    
    
class CandidateRegistrationValidator(serializers.Serializer):
    full_name = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Full Name is Required',
        'null':'Full Name cannot be null',
        'blank':'Full Name cannot be Blank',
    })
    email = serializers.EmailField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Email is Required',
        'null':'Email cannot be null',
        'blank':'Email cannot be Blank',
        'invalid': 'Enter a valid email address'
    })
    password = serializers.CharField(required=True,allow_null=False,allow_blank=False,write_only=True,min_length=6,error_messages={
        'required':'Password is Required',
        'null':'Password cannot be null',
        'blank':'Password cannot be Blank',
        'min_length': 'Password must be at least 6 characters'
    })
    mobile = serializers.CharField(required=False,allow_null=True,allow_blank=True)
    role = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Role is Required',
        'null':'Role cannot be null',
        'blank':'Role cannot be Blank',
    })
    location = serializers.CharField(required=True,allow_null=False,allow_blank=False,error_messages={
        'required':'Location is Required',
        'null':'Location cannot be null',
        'blank':'Location cannot be Blank',
    })
    current_job_title = serializers.CharField(required=False,allow_null=True,allow_blank=True)
    total_experience = serializers.IntegerField(required=False,allow_null=True)
    profile_photo = serializers.ImageField(required=False,allow_null=True,error_messages={
        'invalid': 'Please upload a valid image file'
    })


    def validate_email(self,value):
        if CustomUserModel.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email Already Exists")
        return value
    
    def validate_mobile(self,value):
        if CustomUserModel.objects.filter(mobile=value).exists():
            raise serializers.ValidationError("Mobile Already Exists")
        return value