import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-12345'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Estados permitidos
    ESTADOS_GASTO = ['PENDIENTE', 'APROBADO', 'CANCELADO', 'PAGADO']
    ESTADOS_PAGO = ['PENDIENTE', 'APROBADO', 'EJECUTADO', 'CANCELADO']
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)