from flask import current_app
from marshmallow import Schema, fields, ValidationError, validates


class RegistrationSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    sudoPassword = fields.Str(required=True)

    @validates("sudoPassword")
    def validate_sudoPassword(self, value):
        if value != current_app.config['SUDO_PASSWORD']:
            raise ValidationError('Sudo password is incorrect')