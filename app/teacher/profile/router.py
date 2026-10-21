from fastapi import APIRouter
from app.teacher.profile.services import *

router =  APIRouter(prefix="/profile")

router.add_api_route("/account_status", get_account_status, methods=["GET"])(get_account_status)

router.add_api_route("/fetch_qaulification_drpdwn", fetch_qaulifications, methods=["GET"])

router.add_api_route("/fetch_subject_drpdwn", fetch_subjects, methods=["GET"])

router.add_api_route("/update", update_profile, method=["PUT"])