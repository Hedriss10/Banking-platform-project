import traceback

from flask import request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource

from src.core.hourspoint import HourspointCore
from src.resource.swagger.factorypayloadsOperational import (
    PayloadFactoryHourspoint,
)
from src.service.response import Response

hourspoint_ns = Namespace("hourspoint", description="Manage Hours Point")

# payloads
pagination_arguments_customer = (
    PayloadFactoryHourspoint.pagination_arguments_parser()
)
payload_add_timepoint = PayloadFactoryHourspoint.add_time_point(hourspoint_ns)
payload_add_justification_for_delay = (
    PayloadFactoryHourspoint.add_justification_for_delay(hourspoint_ns)
)
payload_add_holiday = PayloadFactoryHourspoint.add_holiday(hourspoint_ns)
payload_add_absence = PayloadFactoryHourspoint.add_absence(hourspoint_ns)
payload_edit_absence = PayloadFactoryHourspoint.edit_absence(hourspoint_ns)
payload_add_vacation = PayloadFactoryHourspoint.add_vacation(hourspoint_ns)
paylad_edit_vaction = PayloadFactoryHourspoint.edit_vacation(hourspoint_ns)


@hourspoint_ns.route("")
class TimePointResourc(Resource):
    @hourspoint_ns.doc(description="Add timepoint")
    @hourspoint_ns.expect(payload_add_timepoint, validate=True)
    @cross_origin()
    def post(self):
        """Add timepoint"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).add_time_point(
                data=request.get_json()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


@hourspoint_ns.route("/justification")
class TimePointResourceID(Resource):
    @hourspoint_ns.doc(description="Add justifcation for delay user")
    @hourspoint_ns.expect(payload_add_justification_for_delay, validate=True)
    @cross_origin()
    def post(self):
        """Add justifcation for delay user"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).add_justification_for_delay(
                data=request.get_json()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


@hourspoint_ns.route("/holiday")
class HolidayManagerResource(Resource):
    @hourspoint_ns.doc(description="Holiday add post")
    @hourspoint_ns.expect(payload_add_holiday, validate=True)
    @cross_origin()
    def post(self):
        """Holiday add post"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).add_holiday(
                data=request.get_json()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )

    @hourspoint_ns.doc(description="List Holiday")
    @hourspoint_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List all holiday"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).list_holiday(
                data=request.args.to_dict()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


@hourspoint_ns.route("/holiday/<int:id>")
class HolidayManagerId(Resource):
    @hourspoint_ns.doc(description="Delete holiday filter by id")
    @cross_origin()
    def delete(self, id: int):
        """Delete holiday filter by id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).delete_holiday(id=id)

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


@hourspoint_ns.route("/abasence")
class AbsenceManager(Resource):
    @hourspoint_ns.doc(description="Add Absence")
    @hourspoint_ns.expect(payload_add_absence, validate=True)
    @cross_origin()
    def post(self):
        """Absence Add Post"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).add_absence(
                data=request.get_json()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )

    @hourspoint_ns.doc(description="List Absence")
    @hourspoint_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List Absence"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).list_absence_resource(
                data=request.args.to_dict()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


@hourspoint_ns.route("/abasence/<int:id>")
class AbsenceManagerId(Resource):
    @hourspoint_ns.doc(description="Edit absence")
    @hourspoint_ns.expect(payload_edit_absence, validate=True)
    @cross_origin()
    def put(self, id: int):
        """Edit abesence"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).edit_absence(
                id=id, data=request.get_json()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


@hourspoint_ns.route("/vacation")
class VacationManager(Resource):
    @hourspoint_ns.doc(description="Vacation Add")
    @hourspoint_ns.expect(payload_add_vacation, validate=True)
    @cross_origin()
    def post(self):
        """Vacation Add"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).add_vacation(
                data=request.get_json()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )

    @hourspoint_ns.doc(description="List vacation apply")
    @hourspoint_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List vacation apply"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).list_vocation_apply(
                data=request.args.to_dict()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


@hourspoint_ns.route("/vacation/<int:id>")
class VacationManagerId(Resource):
    @hourspoint_ns.doc(description="Edit vacation filter by id")
    @hourspoint_ns.expect(paylad_edit_vaction, validate=True)
    @cross_origin()
    def put(self, id: int):
        """Edit vacation filter by id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).edit_vacation(
                id=id, data=request.get_json()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )

    @hourspoint_ns.doc(description="Delete vaction filter by")
    @cross_origin()
    def delete(self, id: int):
        """Delete vacation delete filter by id"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).delete_vaction(id=id)

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


@hourspoint_ns.route("/list-days-off")
class ListDayOffsManagerResource(Resource):
    @hourspoint_ns.doc(description="List days offs")
    @hourspoint_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List days offs"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).list_day_offs(
                data=request.args.to_dict()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


@hourspoint_ns.route("/list-works-orvertime")
class ListWorksHoursOrvetime(Resource):
    @hourspoint_ns.doc(description="List works hours orvertime")
    @hourspoint_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List works hours orvertime"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).list_works_hours_overtime(
                data=request.args.to_dict()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


@hourspoint_ns.route("/list-works-delay")
class ListWorksHoursOrvetimeDelay(Resource):
    @hourspoint_ns.doc(description="List works delay")
    @hourspoint_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List works delay"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(user_id=user_id).list_works_delay(
                data=request.args.to_dict()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )


@hourspoint_ns.route("/list-works-delay-employess")
class ListRankingUserDelayedWorksEmployess(Resource):
    @hourspoint_ns.doc(description="List ranking user delayed works employess")
    @hourspoint_ns.expect(pagination_arguments_customer, validate=True)
    @cross_origin()
    def get(self):
        """List ranking user delayed works employess"""
        try:
            user_id = request.headers.get("Id", request.environ.get("Id"))
            return HourspointCore(
                user_id=user_id
            ).list_ranking_user_delayed_works_employess(
                data=request.args.to_dict()
            )

        except Exception as e:
            return Response().response(
                status_code=400,
                error=True,
                message_id="something_went_wrong",
                exception=str(e),
                traceback=traceback.format_exc(e),
            )
