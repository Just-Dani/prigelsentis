from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from pymongo import MongoClient
from bson import ObjectId
import secrets

# Inisialisasi Flask-Bcrypt
bcrypt = Bcrypt()

# Inisialisasi Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'main.login' # Menentukan rute login jika pengguna tidak terautentikasi

# Mendefinisikan kelas User untuk Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password = user_data['password'] # Sebaiknya tidak menyimpan password di sini dalam aplikasi nyata

    def get_id(self):
        return self.id

# Fungsi user_loader untuk Flask-Login
@login_manager.user_loader
def load_user(user_id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.db_analisis_sentimen
    users_collection = db.users
    # Mencari pengguna berdasarkan ID
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets.token_hex(16) # Kunci rahasia untuk sesi Flask

    # Inisialisasi ekstensi dengan aplikasi Flask
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # IMPOR BLUEPRINT DI SINI SETELAH APLIKASI DAN EKSTENSI DIINISIALISASI
    # Ini penting untuk menghindari circular import dan memastikan Blueprint terdaftar dengan benar
    from app.routes import bp as main_blueprint
    app.register_blueprint(main_blueprint) # Menggunakan Blueprint untuk rute

    return app

