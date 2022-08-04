import datetime
import json
from json.decoder import JSONDecodeError

from marshmallow import Schema, fields, validate, ValidationError, pre_load


class UploadDataSchema(Schema):
    time_to_live = fields.TimeDelta(
        fields.TimeDelta.DAYS,
        validate=validate.Range(
            min=datetime.timedelta(days=1),
            max=datetime.timedelta(days=7),
        ),
        required=True
    )
    encryption_method = fields.String(
        required=True,
        allow_none=True
    )
    email = fields.Email(
        required=False
    )


class UploadSchema(Schema):
    file = fields.Raw(type='file', required=True)
    data = fields.Nested(UploadDataSchema, required=True)

    @pre_load
    def data_loads(self, in_data, **kwargs):
        data = in_data.get('data')
        if isinstance(data, str):
            try:
                in_data['data'] = json.loads(data)
            except JSONDecodeError:
                raise ValidationError(
                    message='Given data is in incorrect format.',
                    field_name='data'
                )
        return in_data
