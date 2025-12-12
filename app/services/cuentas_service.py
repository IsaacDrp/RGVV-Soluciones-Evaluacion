from app.models.entities import CuentaBancaria, Pago
from app import db

class CuentasService:
    
    @staticmethod
    def crear_cuenta(nombre_banco, nombre_cuenta, numero_cuenta, saldo_inicial, moneda='MXN'):
        """Crea una nueva cuenta bancaria"""
        if saldo_inicial < 0:
            raise ValueError("El saldo inicial no puede ser negativo")
        
        cuenta = CuentaBancaria(
            nombre_banco=nombre_banco,
            nombre_cuenta=nombre_cuenta,
            numero_cuenta=numero_cuenta,
            saldo=saldo_inicial,
            moneda=moneda
        )
        
        db.session.add(cuenta)
        db.session.commit()
        return cuenta
    
    @staticmethod
    def obtener_saldo_total():
        """Calcula el saldo total de todas las cuentas"""
        cuentas = CuentaBancaria.query.all()
        return sum(cuenta.saldo for cuenta in cuentas)
    
    @staticmethod
    def calcular_saldo_teorico():
        """
        Calcula el saldo teórico:
        Saldo Inicial Total - Suma de Pagos Ejecutados
        """
        # Saldo inicial total
        saldo_inicial_total = db.session.query(
            db.func.sum(CuentaBancaria.saldo)
        ).scalar() or 0
        
        # Suma de pagos ejecutados
        pagos_ejecutados = db.session.query(
            db.func.sum(Pago.monto)
        ).filter(Pago.estado == 'EJECUTADO').scalar() or 0
        
        return {
            'saldo_inicial_total': saldo_inicial_total,
            'pagos_ejecutados_total': pagos_ejecutados,
            'saldo_teorico': saldo_inicial_total - pagos_ejecutados
        }
    
    @staticmethod
    def obtener_cuentas_con_saldo_suficiente(monto_requerido):
        """Obtiene cuentas con saldo suficiente para un monto dado"""
        return CuentaBancaria.query.filter(
            CuentaBancaria.saldo >= monto_requerido
        ).all()