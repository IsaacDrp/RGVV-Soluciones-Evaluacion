from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Gasto, Pago, CuentaBancaria
from datetime import datetime
import os
from dotenv import load_dotenv

app = Flask(__name__)

# variables de entorno desde archivo .env
load_dotenv()

# Configuración de base de datos
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///rgv_finanzas.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'clave_secreta_rgv_examen_dev')


app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
db.init_app(app)

with app.app_context():
    db.create_all()

# --- RUTAS DE VISTAS (DASHBOARD) ---

@app.route('/')
def index():
    gastos = Gasto.query.order_by(Gasto.fecha_creacion.desc()).all()
    pagos = Pago.query.order_by(Pago.fecha_creacion.desc()).all()
    cuentas = CuentaBancaria.query.all()
    total_bancos = sum(c.saldo for c in cuentas)
    return render_template('base.html', gastos=gastos, pagos=pagos, cuentas=cuentas, total_bancos=total_bancos)

# --- RUTAS DE GASTOS ---

@app.route('/gasto/crear', methods=['POST'])
def crear_gasto():
    solicitante = request.form['solicitante']
    concepto = request.form['concepto']
    monto = request.form['monto']

    if float(monto) <= 0:
        flash('El monto debe ser mayor a cero.', 'danger')
        return redirect(url_for('index'))
    
    nuevo_gasto = Gasto(solicitante=solicitante, concepto=concepto, monto=monto)
    db.session.add(nuevo_gasto)
    db.session.commit()
    
    flash('Gasto registrado correctamente.', 'success')
    return redirect(url_for('index'))

@app.route('/gasto/<int:id>/accion', methods=['POST'])
def accion_gasto(id):
    gasto = Gasto.query.get_or_404(id)
    accion = request.form['accion'] 
    
    if accion == 'aprobar':
        gasto.estado = 'APROBADO'
        flash(f'Gasto "{gasto.concepto}" aprobado. Listo para pagar.', 'success')
    elif accion == 'cancelar':
        gasto.estado = 'CANCELADO'
        gasto.motivo_cancelacion = "Cancelado manualmente por el usuario"
        flash('Gasto cancelado.', 'warning')
        
    db.session.commit()
    return redirect(url_for('index'))

# --- RUTAS DE PAGOS (LA PARTE CLAVE DEL EXAMEN) ---
@app.route('/gasto/<int:id>/generar_pago', methods=['GET', 'POST'])
def generar_pago(id):
    gasto = Gasto.query.get_or_404(id)
    
    # 1. Validación básica de estado del gasto
    if gasto.estado != 'APROBADO':
        flash('Solo se pueden pagar gastos APROBADOS.', 'danger')
        return redirect(url_for('index'))

    # 2. Verificamos si ya existe un pago pendiente para este gasto
    pago_existente = Pago.query.filter_by(gasto_id=id, estado='PENDIENTE').first()
    if pago_existente:
        flash(f'Error: Ya existe una orden de pago pendiente para el gasto "{gasto.concepto}". Debes ejecutarla o cancelarla primero.', 'warning')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        cuenta_id = request.form['cuenta_id']
        
        nuevo_pago = Pago(
            gasto_id=gasto.id,
            cuenta_id=cuenta_id,
            monto=gasto.monto,
            estado='PENDIENTE', 
            fecha_programada=datetime.utcnow() 
        )
        db.session.add(nuevo_pago)
        db.session.commit()
        
        flash('Pago generado correctamente. Requiere Ejecución.', 'info')
        return redirect(url_for('index'))
    
    cuentas = CuentaBancaria.query.all()
    return render_template('generar_pago.html', gasto=gasto, cuentas=cuentas)


# Paso 2: Ejecutar el Pago
@app.route('/pago/<int:id>/ejecutar', methods=['POST'])
def ejecutar_pago(id):
    pago = Pago.query.get_or_404(id)
    accion = request.form.get('accion') 

    if accion == 'cancelar':
        pago.estado = 'CANCELADO'
        pago.motivo_cancelacion = "Cancelado manualmente"
        pago.gasto.estado = 'APROBADO' 
        db.session.commit()
        flash('Pago cancelado y gasto liberado.', 'warning')
        return redirect(url_for('index'))
    
    cuenta = CuentaBancaria.query.get(pago.cuenta_id)
    
    if cuenta.saldo >= pago.monto:
        cuenta.saldo -= pago.monto
        pago.estado = 'EJECUTADO'
        pago.fecha_ejecucion = datetime.utcnow()
        pago.gasto.estado = 'PAGADO' 
        
        db.session.commit()
        flash(f'Transacción Exitosa. Nuevo saldo: ${cuenta.saldo}', 'success')
    else:
        pago.estado = 'CANCELADO'
        pago.motivo_cancelacion = "Fondos Insuficientes"
        pago.gasto.estado = 'APROBADO'
        
        db.session.commit()
        flash('Fallo de dispersión: Fondos insuficientes.', 'danger')
        
    return redirect(url_for('index'))

# --- UTILIDAD: DATOS DE PRUEBA ---
@app.route('/setup')
def setup():
    try:
        db.session.query(Pago).delete()
        db.session.query(Gasto).delete()
        db.session.query(CuentaBancaria).delete()
        db.session.commit()

        c1 = CuentaBancaria(nombre_banco="BBVA", nombre_cuenta="Nómina", numero_cuenta="123456", saldo=50000)
        c2 = CuentaBancaria(nombre_banco="Banamex", nombre_cuenta="Caja Chica", numero_cuenta="987654", saldo=2000)
        
        db.session.add_all([c1, c2])
        db.session.commit()
        
        flash('Sistema reiniciado.', 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al resetear: {str(e)}', 'danger')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)