from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_superuser
        )
    
class IsRecruiter(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'recruiter'
        )
    
class IsCandidate(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'candidate'
        )
    