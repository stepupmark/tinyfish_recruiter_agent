import requests
import environ
from rest_framework.response import Response
from core.utlis import error_response
from rest_framework import status


env = environ.Env()

INTERVIEW_MODULE_MODEL=env('INTERVIEW_MODULE_MODEL')


def start_interview(resume):
    try:
        if not resume:
            return {"success": False, "error": "Resume not found"}

        with resume.open('rb') as f:
            files = {
                'file': (resume.name, f, "application/pdf")
            }

            response = requests.post(
                INTERVIEW_MODULE_MODEL,
                files=files,
                timeout=10  # ✅ important
            )

        return {
            "success": True,
            "url":INTERVIEW_MODULE_MODEL,
            "data": response.json() if response.content else None
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }