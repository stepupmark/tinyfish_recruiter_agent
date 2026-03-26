from django.db import models
from authentication.models import (
                            CustomUserModel,
                            CommonModel,

                        )

# Create your models here.
class CandidateProfile(CommonModel):
    user = models.OneToOneField(CustomUserModel,on_delete=models.CASCADE,related_name="candidate_profile")
    location = models.CharField(max_length=200,null=True,blank=True)
    current_job_title = models.CharField(max_length=200, null=True, blank=True)
    total_experience = models.CharField(max_length=50, null=True, blank=True)
    profile_photo = models.ImageField(upload_to="candidate_photos/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.full_name}- Current JOB Role {self.current_job_title}"
    
    class Meta:
        db_table='candidateprofile'
        verbose_name = 'CandidateProfile'
        verbose_name_plural = 'CandidateProfiles'
        ordering = ["-created_at"]


class CandidateResume(CommonModel):
    candidate = models.ForeignKey(CandidateProfile,on_delete=models.CASCADE,related_name="resumes")
    resume = models.FileField(upload_to="candidate_resumes/")
    resume_title = models.CharField(max_length=200, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.candidate.user.full_name}- Resume"
    
    class Meta:
        db_table='candidateresume'
        verbose_name = 'CandidateResume'
        verbose_name_plural = 'CandidateResumes'
        ordering = ["-created_at"]
