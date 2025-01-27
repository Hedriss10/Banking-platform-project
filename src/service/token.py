import traceback
from functools import wraps
from flask import request, jsonify
from src.db.pg import PgAdmin
from src.service.response import Response

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        token = token.replace('Bearer ', '')

        try:
            query = f""" SELECT id FROM public.user WHERE session_token = '{token}'; """
            result = PgAdmin().fetch_to_dict(query=query)

            if not result:
                return Response().response(status_code=401, error=True, message_id="Invalid token", exception=str(), traceback=traceback.format_exc())
            
            request.user_id = result[0]["id"]

        except Exception as e:
            return Response().response(status_code=500, error=True, message_id="Token_is_required", exception=str(), traceback=traceback.format_exc())

        return f(*args, **kwargs)

    return decorated