from datetime import datetime

from flask import Blueprint, abort, current_app, jsonify, request
from markupsafe import escape

from app.util import get_current_url

tostartdate = Blueprint("tostartdate", __name__, url_prefix="/tostartdate")


@tostartdate.route("/<questionnaire>")
def get_to_start_date_for_questionnaire(questionnaire: str):
    to_start_date = current_app.datastore.get_to_start_date(questionnaire)
    if to_start_date is None:
        current_app.logger.error(f"No TO Start date found for {questionnaire}")
        abort(404, description=f"No data found for {questionnaire}")
    current_app.logger.info(
        f"Date returned {jsonify(to_start_date)} for {questionnaire}"
    )
    return jsonify(to_start_date), 200


@tostartdate.route("/<questionnaire>", methods=["POST"])
def create_to_start_date_for_a_questionnaire(questionnaire: str):
    formatted_date = get_formatted_date(request)

    to_start_date = current_app.datastore.get_to_start_date(questionnaire)
    if to_start_date is not None:
        current_app.logger.error(
            (
                f"{questionnaire} already has a start date {to_start_date}. "
                f"Path end point required"
            )
        )
        abort(
            409,
            description=(
                f"{questionnaire} already has a TO start date {to_start_date}. "
                f"Please use the Patch end point "
                f"to update the TO start date"
            ),
        )

    current_app.datastore.add_to_start_date(questionnaire, formatted_date)
    current_url = get_current_url(request)
    current_app.logger.info(
        f"Created start date for {questionnaire} : {formatted_date}"
    )
    return jsonify({"location": f"{current_url}/tostartdate/{questionnaire}"}), 201


@tostartdate.route("/<questionnaire>", methods=["PATCH"])
def update_to_start_date_for_a_questionnaire(questionnaire: str):
    formatted_date = get_formatted_date(request)

    to_start_date = current_app.datastore.get_to_start_date(questionnaire)
    if to_start_date is None:
        current_app.logger.error(f"No data found for {questionnaire} unable to update")
        abort(
            400,
            description=(
                f"No data found for {questionnaire}, "
                f"please use the create end point"
            ),
        )

    current_app.datastore.add_to_start_date(questionnaire, formatted_date)
    current_url = get_current_url(request)
    current_app.logger.info(f"{questionnaire} updated to {to_start_date}")
    return jsonify({"location": f"{current_url}/tostartdate/{questionnaire}"}), 200


@tostartdate.route("/<questionnaire>", methods=["DELETE"])
def delete_to_start_date_from_questionnaire(questionnaire):
    to_start_date = current_app.datastore.get_to_start_date(questionnaire)
    if to_start_date is None:
        current_app.logger.error(f"No instrument found {questionnaire}")
        abort(404, description=f"No data found for {questionnaire}")
    current_app.datastore.delete_to_start_date(questionnaire)
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

    if "tostartdate" not in request_data:
        current_app.logger.error("tostartdate not provided")
        abort(400, description="tostartdate is required, in format yyyy-mm-dd")
    to_start_date = request_data["tostartdate"]

    try:
        formatted_date = datetime.strptime(to_start_date, "%Y-%m-%d")
    except ValueError:
        current_app.logger.error("tostartdate not in the correct format")
        abort(400, description="Date is not in the required format yyyy-mm-dd")

    return formatted_date
