from django.contrib import admin
from .models import (
    CandidateProfile,
    CandidateResume,
)

# Register your models here.
admin.site.register(CandidateProfile)
admin.site.register(CandidateResume)