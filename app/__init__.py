import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_socketio import SocketIO
from app.main.extensions import socketio

from app.main.service.user_service import UserService
def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure SocketIO explicitly
    app.config['SECRET_KEY'] = 'your_secret_key'  # Add a secret key

    from app.main.extensions import db, socketio
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")  # Ensure SocketIO is initialized with the app

    app.extensions['db'] = db

    with app.app_context():
        from app.main.model.user import User
        db.create_all()

    user_service = UserService(db)
    app.extensions['user_service'] = user_service

    cwd = os.getcwd()
    print(cwd)
    data_dir = os.path.join(cwd, "uploads")
    print(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    app.config['data_dir'] = os.path.join(data_dir)
    app.config['image_prefix_size'] = 8

    @app.route("/", methods=['GET'])
    def index():
        return jsonify({"url_map": app.url_map.__str__()}), 200

    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            response = Response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
            response.status_code = 204  # No Content
            return response


    def add_cors_headers(response: Response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    app.after_request(add_cors_headers)

    from app.main import main_bp as main_bp
    app.register_blueprint(main_bp)

    app.route("/test-cors", methods=["GET", "OPTIONS"])
    def test_cors():
        return jsonify({"message": "CORS is working"}), 200


    return app

def run_app():
    app = create_app()
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, use_reloader=False)

if __name__ == '__main__':
    run_app()

app = create_app()
