from django.db import models
from django.utils.translation import gettext_lazy as _

class UserRoles(models.TextChoices):
    ADMIN = 'superadmin', _('Superadmin') 
    RECRUITER = 'recruiter', _('Recruiter')
    CANDIDATE = 'candidate', _('Candidate')


class UserStatusChoices(models.TextChoices):
    ACTIVE = 'active', _('Active')
    INACTIVE = 'in_active', _("In Active")


class EmploymentTypeChoices(models.TextChoices):
    FULLTIME = 'full_time', _('Full Time')
    PARTTIME = 'part_time', _('Part Time')
    INTERNSHIP = 'internship', _('Intership')


class ApplicationStatus(models.TextChoices):
    APPLIED = 'applied', _('Applied')
    SHORTLISTED = 'shortlisted', _('Shortlisted')
    REJECTED = 'rejected', _('Rejected')
    HIRED = 'hired', _('Hired')