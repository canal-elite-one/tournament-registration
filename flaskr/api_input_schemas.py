from marshmallow import Schema, fields, validate

"""
Schemas in this file are here to validate json payload for api requests.
They only check for presence and correct formatting of field,
as well as static value checking. They do not do dynamic value checking,
i.e. they do not ensure consistency between different columns or table in the db.
"""


class MakePaymentSchema(Schema):
    category_ids = fields.List(
        fields.Str,
        data_key="categoryIds",
        required=True,
        allow_none=False,
    )
    total_actual_paid = fields.Int(
        data_key="totalActualPaid",
        required=True,
        allow_none=False,
        validate=validate.Range(min=0),
    )


class CategoryIdsSchema(Schema):
    category_ids = fields.List(
        fields.Str,
        data_key="categoryIds",
        required=True,
        allow_none=False,
    )
