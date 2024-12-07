# app/main/blueprints/chat.py
from flask import Blueprint, current_app, jsonify
from flask_socketio import SocketIO, emit
from jinja2.utils import Namespace
from app.main.extensions import socketio
from app.main.service.user_service import UserService
import logging
from app.main.model.chat import message_history

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/get_history', methods=['GET'])
def get_history():
    return jsonify({"messages": message_history})

@socketio.on('connect', namespace='/chat')
def handle_connect():
    logger.info('Client connected to chat namespace')

@socketio.on('authenticate', namespace='/chat')
def authenticate(data):
    try:
        token = data.get('token')
        if not token:
            emit('auth_error', {'message': 'No token provided'})
            return

        with current_app.app_context():
            user_service: UserService = current_app.extensions['user_service']
            user = user_service.find_by_token(token)

            if not user:
                emit('auth_error', {'message': 'Invalid token'})
                return

        emit('auth_success', {'username': user.username})
    except Exception as e:
        logger.exception('Error in authenticate event handler')
        emit('auth_error', {'message': 'Internal server error'})


@socketio.on('send_message', namespace='/chat')
def handle_message(data):
    token = data.get('token')
    message = data.get('message')

    logger.info(f'Received message data: {data}')

    if not token or not message:
        logger.warning('Invalid message data')
        return {'status': 'error', 'message': 'Invalid message data'}

    # Validate user
    with current_app.app_context():
        user_service: UserService = current_app.extensions['user_service']
        user = user_service.find_by_token(token)

        if user is None:
            logger.warning('Unauthorized message attempt')
            return {'status': 'error', 'message': 'Unauthorized'}

        username = user.username

    message_data = {
        'username': username,
        'message': message
    }

    logger.info(f'Processing message from {username}: {message}')

    message_history.insert(0, message_data)
    if len(message_history) > 100:
        message_history.pop(0)

    emit('receive_message', message_data, broadcast=True)

    return {'status': 'success'}
