from flask import Flask
from air_sensor_service import air_blueprint
from crowd_sensor_service import crowd_blueprint
from water_sensor_service import water_sensor_bp
from room_sensor_service import room_sensor_bp
from solar_sensor_service import solar_sensor_bp
from booking_service import booking_bp
from request_logging_service import request_logging_bp
from quality_checking_service import environment_quality_bp

app = Flask(__name__)

# Register blueprints for each microservice
app.register_blueprint(air_blueprint, url_prefix='/air')
app.register_blueprint(crowd_blueprint, url_prefix='/crowd')
app.register_blueprint(water_sensor_bp, url_prefix='/water')
app.register_blueprint(room_sensor_bp, url_prefix='/room')
app.register_blueprint(solar_sensor_bp, url_prefix='/solar')
app.register_blueprint(booking_bp, url_prefix='/booking')
app.register_blueprint(request_logging_bp, url_prefix='/log')
app.register_blueprint(environment_quality_bp, url_prefix='/environment')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
