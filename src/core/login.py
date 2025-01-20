from src.models.user import User
from flask import jsonify

class LoginCore:
    def __init__(self, user_id = None, *args, **kwargs) -> None:
        self.user_id = user_id
        
        
    def login_user(self, data: dict):
        try:
            if not data.get("email"):
                return jsonify({"error": "Email is required"}), 400
            
            user = User.query.filter_by(email=data.get("email")).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            return jsonify({"success": True}), 200     
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    
    def rest_password(self, data: dict):
        try:
            if not data.get("email"):
                return jsonify({"error": "Email is required"}), 400
            
            user = User.query.filter_by(email=data.get("email")).first()
            if not user:
                return jsonify ({"error": "User not found"}), 404
            
            return jsonify({"success": True}), 200     
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500