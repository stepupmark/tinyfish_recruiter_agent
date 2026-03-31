from django.db import models
from authentication.models import (
                    CommonModel,
                    CustomUserModel
                )

from core.choice_fields import (
                    EmploymentTypeChoices,
                    UserStatusChoices,
                    ApplicationStatus,
                    InterviewStatus,
                )



# Create your models here.


class Recruiter(CommonModel):
    user = models.OneToOneField(CustomUserModel,on_delete=models.CASCADE,related_name="recruiter")
    company_name = models.CharField(max_length=200)
    company_email = models.EmailField(null=True,blank=True,unique=True)
    gst_number = models.CharField(max_length=15, null=True, blank=True)
    pan_number = models.CharField(max_length=10, null=True, blank=True)
    company_registration_number = models.CharField(max_length=50, null=True, blank=True)

    # Address Fields
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, default="India")
    pincode = models.CharField(max_length=10, null=True, blank=True)

    # Company Profile
    company_website = models.URLField(null=True, blank=True)
    company_size = models.CharField(max_length=50, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    company_description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10,choices=UserStatusChoices.choices,default=UserStatusChoices.ACTIVE)

    is_verified = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.company_name}-{self.company_email}-{self.city}"
    
    class Meta:
        db_table = "recruiters"
        verbose_name = "Recruiter"
        verbose_name_plural = "Recruiters"
        ordering = ["-created_at"]


class JobPosting(CommonModel):
    recruiter = models.ForeignKey(Recruiter,on_delete=models.CASCADE,related_name="job_postings")

    # Job DETAILS
    job_title = models.CharField(max_length=200)
    job_description = models.TextField(null=True,blank=True)
    job_description_file = models.FileField(upload_to="recruiters/job_descriptions/",null=True,blank=True)
    job_location = models.CharField(max_length=200)
    employment_type = models.CharField(max_length=50,choices=EmploymentTypeChoices.choices,default=EmploymentTypeChoices.FULLTIME)
    salary_range = models.CharField(max_length=100, null=True, blank=True)

    skills_required = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20,choices=UserStatusChoices.choices,default=UserStatusChoices.ACTIVE)


    def __str__(self):
        return f"{self.recruiter.user.full_name} - {self.job_title}"
    
    class Meta:
        db_table = "jobpostings"
        verbose_name = "JobPosting"
        verbose_name_plural = "JobPostings"
        ordering = ["-created_at"]


class JobApplication(CommonModel):
    job = models.ForeignKey(JobPosting,on_delete=models.CASCADE,related_name="applications",db_index=True)
    user = models.ForeignKey(CustomUserModel,on_delete=models.CASCADE,related_name="user_job_application")
    resume = models.FileField(upload_to="resumes/")
    application_status = models.CharField(max_length=20,choices=ApplicationStatus.choices,default=ApplicationStatus.APPLIED)


    def __str__(self):
        return f"{self.job.job_title} - {self.user.full_name}"
    
    class Meta:
        db_table='jobapplication'
        verbose_name = 'JobApplication'
        verbose_name_plural = 'JobApplications'
        ordering = ["-created_at"]



class InterviewSchedule(CommonModel):
    job = models.ForeignKey(JobPosting,on_delete=models.CASCADE,related_name="job_interviews")
    application = models.ForeignKey(JobApplication,on_delete=models.CASCADE,related_name="job_application_interviews")
    candidate = models.ForeignKey(CustomUserModel,on_delete=models.CASCADE,related_name="candidate_interview")

    interview_date = models.DateField()
    interview_time = models.TimeField()

    interview_status = models.CharField(max_length=20,choices=InterviewStatus.choices,default=InterviewStatus.SCHEDULED)
    notes = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.job.job_title} - {self.candidate.full_name} - {self.interview_date}- Time {self.interview_time}"
    
    class Meta:
        db_table='interviewschedule'
        verbose_name = 'InterviewSchedule'
        verbose_name_plural = 'InterviewSchedules'
        ordering = ["-created_at"]