from django.contrib import admin
from recruiter.models import Recruiter, JobApplication,JobPosting,InterviewSchedule
# Register your models here.


admin.site.register(Recruiter)
admin.site.register(JobPosting)
admin.site.register(JobApplication)
admin.site.register(InterviewSchedule)