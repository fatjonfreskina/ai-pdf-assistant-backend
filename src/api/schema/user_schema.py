from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.String(dump_only=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
