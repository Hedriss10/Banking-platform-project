from flask import request
from os import environ


class Response():

    def default_response_message(self, data, metadata, message_id, error):
        return {
            "data": data, "metadata": metadata, "message_id": message_id, "error": error
        }
        
    def response(self, status_code, data={}, metadata={}, message_id="", error=False, exception="", traceback=""):
        response = self.default_response_message(data, metadata, message_id, error)

        if status_code >= 400:
            print(traceback)

        try:
            if environ["FLASK_ENV"] != "development" and "production" and status_code >= 400:
                response["traceback"] = traceback
                user_id = request.headers.get("custom:_id", request.environ.get("custom:_id", 0))
                session_id = request.headers.get("x-sid", "")

                response.pop("traceback")
        except Exception as e:
            print("Tracker Logger: ", e)

        return response, status_code