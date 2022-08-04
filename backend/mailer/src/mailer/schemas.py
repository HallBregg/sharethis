from marshmallow import Schema, fields


class NewUploadSchema(Schema):
    email = fields.Email(required=True)
    url = fields.URL(required=True)


class UploadDownloadedSchema(Schema):
    recipients = fields.List(fields.Email, required=True)
    url = fields.URL(required=True)
