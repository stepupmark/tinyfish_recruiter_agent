from rest_framework.permissions import BasePermission

class IsRecruiter(BasePermission):
    message = "User is not a recruiter"

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False
        
        return  hasattr(user,"recrutier") and user.recruiter is not None