from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from datetime import datetime, timezone

class MetricSchema(Schema):
    class Meta:
        fields = ('name', 'value', 'timestamp')

    name = fields.Str(required=True)
    value = fields.Float(required=True)
    timestamp = fields.DateTime(missing=lambda: datetime.utcnow())

class AggregatedMetricSchema(Schema):
    class Meta:
        fields = ('_id', 'average_value')
from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from datetime import datetime, timezone

class MetricsRequestSchema(Schema):
    name = fields.Str(required=True)
    startDate = fields.Str(allow_none=True)  # Allow null values
    endDate = fields.Str(allow_none=True)    # Allow null values
    interval = fields.Str(required=True)
    include_zeros = fields.Bool(missing=False)

    @validates('interval')
    def validate_interval(self, value):
        valid_intervals = ['minute', 'hour', 'day']
        if value.lower() not in valid_intervals:
            raise ValidationError(f'Invalid interval. Supported intervals: {", ".join(valid_intervals)}')

    @validates_schema
    def validate_dates(self, data, **kwargs):
        start_date = (
            datetime.fromisoformat(data['startDate']).replace(tzinfo=timezone.utc)
            if data['startDate'] is not None
            else datetime.min.replace(tzinfo=timezone.utc)
        )
        end_date = (
            datetime.fromisoformat(data['endDate']).replace(tzinfo=timezone.utc)
            if data['endDate'] is not None
            else datetime.max.replace(tzinfo=timezone.utc)
        )

        if start_date > end_date:
            raise ValidationError("Start date must be less than or equal to end date.")
