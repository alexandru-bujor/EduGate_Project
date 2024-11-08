from flask import Flask
from config import Config
from routes.attendance import attendance_bp
from routes.auth import auth_bp
from routes.class_management import class_management_bp
from routes.dashboard import dashboard_bp
from routes.index import index_bp
from routes.links import links
from routes.search import search
from routes.user_management import user_management_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(attendance_bp, url_prefix='/attendance')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(class_management_bp, url_prefix='/class_management')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(index_bp, url_prefix='/')  # Assuming index is the root
app.register_blueprint(links, url_prefix='/links')
app.register_blueprint(search, url_prefix='/search')
app.register_blueprint(user_management_bp, url_prefix='/user_management')


if __name__ == '__main__':
    app.run(debug=True)
