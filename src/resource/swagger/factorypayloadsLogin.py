from flask_restx import fields


class PayloadFactoryLogin:
    @staticmethod
    def login_platform_payload(api):
        return api.model(
            "Login",
            {
                "email": fields.String(example="", required=True),
                "password": fields.String(example="********", required="True"),
            },
        )

    @staticmethod
    def reset_login_paylaod(api):
        return api.model(
            "LoginRest",
            {
                "email": fields.String(example="", required=True),
                "password": fields.String(example="********", required="True"),
            },
        )

    @staticmethod
    def reset_master_password(api):
        return api.model(
            "ResetMasterPassword",
            {"id": fields.Integer(example=3, required=True)},
        )
