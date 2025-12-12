from datetime import datetime
from app import db

class Gasto(db.Model):
    __tablename__ = 'gasto'
    
    id = db.Column(db.Integer, primary_key=True)
    solicitante = db.Column(db.String(100), nullable=False)
    concepto = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='PENDIENTE')
    motivo_cancelacion = db.Column(db.String(300))
    
    # Relaciones
    pagos = db.relationship('Pago', backref='gasto', lazy=True)
    
    def __repr__(self):
        return f'<Gasto {self.id}: {self.concepto}>'

class Pago(db.Model):
    __tablename__ = 'pago'
    
    id = db.Column(db.Integer, primary_key=True)
    gasto_id = db.Column(db.Integer, db.ForeignKey('gasto.id'), nullable=False)
    cuenta_id = db.Column(db.Integer, db.ForeignKey('cuenta_bancaria.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_ejecucion = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default='PENDIENTE')
    notas = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<Pago {self.id}: ${self.monto}>'

class CuentaBancaria(db.Model):
    __tablename__ = 'cuenta_bancaria'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_banco = db.Column(db.String(100), nullable=False)
    nombre_cuenta = db.Column(db.String(100), nullable=False)
    numero_cuenta = db.Column(db.String(50), nullable=False, unique=True)
    saldo = db.Column(db.Float, default=0.0)
    moneda = db.Column(db.String(10), default='MXN')
    
    # Relaciones
    pagos = db.relationship('Pago', backref='cuenta', lazy=True)
    
    def __repr__(self):
        return f'<Cuenta {self.nombre_cuenta}>'