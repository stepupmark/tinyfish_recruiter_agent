from django.db import models
from django.utils.translation import gettext_lazy as _

class UserRoles(models.TextChoices):
    ADMIN = 'superadmin', _('Superadmin') 
    RECRUITER = 'recruiter', _('Recruiter')
    CANDIDATE = 'candidate', _('Candidate')


class UserStatusChoices(models.TextChoices):
    ACTIVE = 'active', _('Active')
    INACTIVE = 'in_active', _("In Active")