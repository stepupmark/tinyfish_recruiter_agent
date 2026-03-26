
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from authentication.models import CustomUserModel
from rest_framework_simplejwt.tokens import RefreshToken

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'  
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'next_page': self.get_next_link(),
            'prev_page': self.get_previous_link(),
            'count': self.page.paginator.count,
            'rows_per_page':self.get_page_size(self.request),
            'results': data
            # **data
        })
    
def success_response(data=None,message="Success"):
    return { 
            "success":True,
            "message":message,
            "data":data
        }

def error_response(errors=None,message="Error"):
    return {
        "success":False,
        "message":message,
        "errors":errors
    }


def get_tokens_for_user(CustomUser: CustomUserModel):
    """
    Generate JWT refresh and access tokens for a given user.

    Adds custom claims (full_name, email, mobile) into the token.

    Args:
        user (User): The user instance for whom to generate tokens.

    Returns:
        dict: A dictionary containing:
            - refresh (str): Refresh token as a string.
            - access (str): Access token as a string.
            - expiry_time (int): Token expiry timestamp in milliseconds.
    """
    token = RefreshToken.for_user(CustomUser)
    token["full_name"] = CustomUser.username
    token["email"] = CustomUser.email
    token["mobile"] = CustomUser.mobile
    return {
        'refresh': str(token),
        'access': str(token.access_token),
        'expiry_time': (token.access_token['exp'] * 1000)
    }
def flatten_errors(errors):
    """Flattens DRF error dict into readable string."""
    if isinstance(errors, dict):
        return {k: v[0] if isinstance(v, list) else v for k, v in errors.items()}
    return str(errors)