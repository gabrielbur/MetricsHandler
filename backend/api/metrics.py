from flask import Blueprint, request, jsonify
from loguru import logger
from datetime import datetime, timezone, timedelta
from collections import OrderedDict
import asyncio
from typing import List, Dict, Tuple, Generator
from flask_socketio import SocketIO
from flask_pymongo import PyMongo
from api.schemas import MetricSchema, MetricsRequestSchema


CACHE_EXPIRATION_TIME = timedelta(minutes=30)
metric_cache: OrderedDict[str, Tuple[List[Dict], datetime]] = OrderedDict()

def cache_key(name: str, start_date: datetime, end_date: datetime, interval: str, include_zeros: bool) -> str:
    return f'{name}_{start_date.isoformat()}_{end_date.isoformat()}_{interval}_{include_zeros}'

def date_range(start_date: datetime, end_date: datetime, increment: timedelta) -> Generator[datetime, None, None]:
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += increment

def fill_missing_dates(data: List[Dict], start_date: datetime, end_date: datetime, interval: str) -> List[Dict]:
    increments = {'day': timedelta(days=1), 'hour': timedelta(hours=1), 'minute': timedelta(minutes=1)}
    formats = {'day': "%Y-%m-%d", 'hour': "%Y-%m-%d %H", 'minute': "%Y-%m-%d %H:%M"}
    time_increment = increments[interval]
    date_format = formats[interval]
    data_dict = {d['_id']: d for d in data}
    return [data_dict.get(date.strftime(date_format), {'_id': date.strftime(date_format), 'average_value': 0})
            for date in date_range(start_date, end_date, time_increment)]

def get_aggregated_metrics(name: str, start_date: datetime, end_date: datetime, interval: str, mongo: PyMongo) -> List[Dict]:
    date_format = {'day': '%Y-%m-%d', 'hour': '%Y-%m-%d %H:00', 'minute': '%Y-%m-%d %H:%M'}.get(interval, '%Y-%m-%d')
    pipeline = [
        {'$match': {'name': name, 'timestamp': {'$gte': start_date, '$lte': end_date}}},
        {'$group': {'_id': {'$dateToString': {'format': date_format, 'date': '$timestamp'}}, 'average_value': {'$avg': '$value'}}},
        {'$sort': {'_id': 1}}
    ]
    try:
        return list(mongo.db.metrics.aggregate(pipeline))
    except Exception as e:
        logger.error(f'MongoDB aggregation error: {e}')
        return []

def init_metrics_module(app, mongo: PyMongo, socketio: SocketIO, login_manager):
    metrics_bp = Blueprint('metrics', __name__)

    @metrics_bp.route('/log_metrics', methods=['POST'])
    def log_metrics():
        metric_schema = MetricSchema()
        try:
            data = metric_schema.load(request.get_json())
            name = data['name']
            value = data['value']
            timestamp = datetime.now(timezone.utc)
            result = mongo.db.metrics.insert_one({
                'name': name, 'value': value, 'timestamp': timestamp
            })
            if result.inserted_id:
                socketio.emit('metrics_update', {'name': name, 'value': value, 'timestamp': timestamp.isoformat()})
                return jsonify({'message': 'Metric logged successfully'}), 200
            else:
                return jsonify({'message': 'Failed to log metric'}), 500
        except Exception as e:
            logger.error(f"Error in /log_metrics route: {e}")
            return jsonify({'message': 'Internal Server Error'}), 500

    @socketio.on('request_metrics')
    def handle_request_metrics(data):
        metrics_request_schema = MetricsRequestSchema()
        try:
            validated_data = metrics_request_schema.load(data)
            metrics_data = get_metrics_data(validated_data, mongo)
            socketio.emit('metrics_data', metrics_data)
        except Exception as e:
            logger.error(f"Error handling request_metrics event: {e}")
            socketio.emit('error', {'message': str(e)})

    @metrics_bp.route('/get_metrics', methods=['POST'])
    def get_metrics():
        metrics_request_schema = MetricsRequestSchema()
        try:
            data = metrics_request_schema.load(request.get_json())
            metrics_data = get_metrics_data(data, mongo)
            return jsonify({'metrics': metrics_data}), 200
        except Exception as e:
            logger.error(f"Error in /get_metrics route: {e}")
            return jsonify({'message': 'Internal Server Error'}), 500

    @metrics_bp.route('/get_metric_names', methods=['GET'])
    def get_metric_names():
        try:
            metric_names = mongo.db.metrics.distinct('name')
            return jsonify(metric_names), 200
        except Exception as e:
            logger.error(f"Error fetching metric names: {e}")
            return jsonify({'message': 'Internal Server Error'}), 500

    app.register_blueprint(metrics_bp, url_prefix='/metrics')
    loop = asyncio.get_event_loop()
    loop.create_task(update_metrics_cache(mongo, socketio))

def get_metrics_data(data: Dict, mongo: PyMongo) -> List[Dict]:
    name = data['name']
    start_date_str = data['startDate']
    end_date_str = data['endDate']
    interval = data['interval']
    include_zeros = data['include_zeros']
    start_date = datetime.fromisoformat(start_date_str).replace(tzinfo=timezone.utc) if start_date_str else datetime.min.replace(tzinfo=timezone.utc)
    end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=timezone.utc) if end_date_str else datetime.max.replace(tzinfo=timezone.utc)
    key = cache_key(name, start_date, end_date, interval, include_zeros)
    if key in metric_cache:
        return metric_cache[key][0]
    metrics_data = get_aggregated_metrics(name, start_date, end_date, interval, mongo)
    if include_zeros:
        metrics_data = fill_missing_dates(metrics_data, start_date, end_date, interval)
    metric_cache[key] = (metrics_data, datetime.now(timezone.utc))
    return metrics_data

async def update_metrics_cache(mongo: PyMongo, socketio: SocketIO):
    while True:
        await asyncio.sleep(300)
        current_time = datetime.now(timezone.utc)
        keys_to_delete = [key for key, (_, timestamp) in metric_cache.items() if current_time - timestamp >= CACHE_EXPIRATION_TIME]
        for key in keys_to_delete:
            del metric_cache[key]
        for key in metric_cache.keys():
            name, start_date_str, end_date_str, interval, include_zeros_str = key.split('_')
            include_zeros = include_zeros_str == 'True'
            start_date = datetime.fromisoformat(start_date_str).replace(tzinfo=timezone.utc)
            end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=timezone.utc)
            new_data = get_aggregated_metrics(name, start_date, end_date, interval, mongo)
            if include_zeros:
                new_data = fill_missing_dates(new_data, start_date, end_date, interval)
            old_data, _ = metric_cache[key]
            if new_data != old_data:
                metric_cache[key] = (new_data, datetime.now(timezone.utc))
                socketio.emit('metrics_update', {'metrics': new_data, 'key': key})
