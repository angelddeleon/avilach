from flask import Flask
from config import Config
from routes import main_routes
from models import db
import os
import logging

app = Flask(__name__)
application = app
app.config.from_object(Config)

# Carpeta para imágenes principales
UPLOAD_FOLDER = 'static/imagenes/inmuebles'  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Carpeta para documentos y cedulas
ARCHIVOS_FOLDER = os.path.join('static', 'archivos')  # NUEVA LINEA

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.config['ARCHIVOS_FOLDER'] = ARCHIVOS_FOLDER  # NUEVA LINEA
# Límite de tamaño para archivos: 2 GB (efectivamente sin límite práctico)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 * 1024  # 2 GB

# Configuración del logger para Flask
logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
# Crear carpeta 'static/archivos' si no existe
os.makedirs(ARCHIVOS_FOLDER, exist_ok=True)  # NUEVA LINEA

# Función para verificar extensiones permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Inicializa la instancia de SQLAlchemy con la aplicación
db.init_app(app)

# Registrar las rutas desde otro archivo
app.register_blueprint(main_routes)

if __name__ == '__main__':
    app.run(debug=True)
