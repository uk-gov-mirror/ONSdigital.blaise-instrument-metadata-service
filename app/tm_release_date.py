from datetime import datetime

from flask import Blueprint, abort, current_app, jsonify, request
from markupsafe import escape

from app.util import get_current_url

tmreleasedate = Blueprint("tmreleasedate", __name__, url_prefix="/tmreleasedate")


@tmreleasedate.route("/<questionnaire>")
def get_tm_release_date_for_questionnaire(questionnaire: str):
    tm_release_date = current_app.datastore.get_tm_release_date(questionnaire)
    if tm_release_date is None:
        current_app.logger.error(f"No TM Release date found for {questionnaire}")
        abort(404, description=f"No data found for {questionnaire}")
    current_app.logger.info(
        f"Date returned {jsonify(tm_release_date)} for {questionnaire}"
    )
    return jsonify(tm_release_date), 200


@tmreleasedate.route("/<questionnaire>", methods=["POST"])
def create_tm_release_date_for_a_questionnaire(questionnaire: str):
    formatted_date = get_formatted_date(request)

    tm_release_date = current_app.datastore.get_tm_release_date(questionnaire)
    if tm_release_date is not None:
        error_msg = (
            f"{questionnaire} already has a Release date {tm_release_date}. "
            "Patch end point required"
        )
        abort(
            409,
            description=(
                f"{questionnaire} already has a TM Release date {tm_release_date}. "
                f"Please use the Patch end point to update the TM Release date"
            ),
        )
        current_app.logger.error(error_msg)

    current_app.datastore.add_tm_release_date(questionnaire, formatted_date)
    current_url = get_current_url(request)
    success_msg = f"Created Release date for {questionnaire} : {formatted_date}"
    current_app.logger.info(success_msg)
    return jsonify({"location": f"{current_url}/tmreleasedate/{questionnaire}"}), 201


@tmreleasedate.route("/<questionnaire>", methods=["PATCH"])
def update_tm_release_date_for_a_questionnaire(questionnaire: str):
    formatted_date = get_formatted_date(request)

    tm_release_date = current_app.datastore.get_tm_release_date(questionnaire)
    if tm_release_date is None:
        current_app.logger.error(f"No data found for {questionnaire} unable to update")
        abort(
            400,
            description=(
                f"No data found for {questionnaire}, "
                f"please use the create end point"
            ),
        )

    current_app.datastore.add_tm_release_date(questionnaire, formatted_date)
    current_url = get_current_url(request)
    current_app.logger.info(f"{questionnaire} updated to {tm_release_date}")
    return jsonify({"location": f"{current_url}/tmreleasedate/{questionnaire}"}), 200


@tmreleasedate.route("/<questionnaire>", methods=["DELETE"])
def delete_tm_release_date_from_questionnaire(questionnaire):
    tm_release_date = current_app.datastore.get_tm_release_date(questionnaire)
    if tm_release_date is None:
        current_app.logger.error(f"No instrument found {questionnaire}")
        abort(404, description=f"No data found for {questionnaire}")
    current_app.datastore.delete_tm_release_date(questionnaire)
    current_app.logger.info(f"{questionnaire} deleted")
    return f"Deleted {escape(questionnaire)}", 204


def get_formatted_date(request_body):
    try:
        request_data = request_body.get_json()
        if request_data is None:
            raise
    except Exception:
        current_app.logger.error("Request was not in JSON format")
        abort(400, description="Requires JSON format")

    if "tmreleasedate" not in request_data:
        current_app.logger.error("tmreleasedate not provided")
        abort(400, description="tmreleasedate is required, in format yyyy-mm-dd")
    tm_release_date = request_data["tmreleasedate"]

    try:
        formatted_date = datetime.strptime(tm_release_date, "%Y-%m-%d")
    except ValueError:
        current_app.logger.error("tmreleasedate not in the correct format")
        abort(400, description="Date is not in the required format yyyy-mm-dd")

    return formatted_date
