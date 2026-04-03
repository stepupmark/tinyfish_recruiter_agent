import requests
import environ
from rest_framework.response import Response
from core.utlis import error_response, success_response
from rest_framework import status
import mimetypes

env = environ.Env()

N8N_MAIL_AUTOMATION = env('RESUME_ANALYSIS_WEBHOOK')

def  candidate_resume_analysis(resume_file,job_description_file):
    try:
        files = {}

        
        if resume_file:
            resume_file.open('rb')  #  MUST open file
            files["resume"] = (
                resume_file.name,
                resume_file,
                "application/pdf"
            )

        
        if job_description_file:
            content_type, _ = mimetypes.guess_type(job_description_file.name)

            files["job_description"] = (
                job_description_file.name,
                job_description_file,
                content_type or "application/octet-stream"  # fallback
            )

        response = requests.post(N8N_MAIL_AUTOMATION, files=files)
        return {
            "success": True,
            "data": response.json() if response.content else None
        }
    except Exception as e:
        return Response(error_response(message="Something went Wrong",errors=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)