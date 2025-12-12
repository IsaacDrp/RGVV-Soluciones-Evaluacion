from datetime import datetime
from app.models.entities import Gasto, Pago, CuentaBancaria
from app import db

class PagoService:
    
    @staticmethod
    def _validar_ejecucion_pago(pago):
        """Validaciones antes de ejecutar un pago"""
        if pago.estado != 'APROBADO':
            return False, f"El pago está en estado {pago.estado}, debe estar APROBADO"
        
        cuenta = CuentaBancaria.query.get(pago.cuenta_id)
        if not cuenta:
            return False, "La cuenta bancaria no existe"
        
        return True, "Validación exitosa"
    
    @staticmethod
    def ejecutar_pago(pago_id):
        """Ejecuta un pago con validación de fondos"""
        pago = Pago.query.get_or_404(pago_id)
        
        # Validación inicial
        valido, mensaje = PagoService._validar_ejecucion_pago(pago)
        if not valido:
            return False, mensaje
        
        cuenta = CuentaBancaria.query.get(pago.cuenta_id)
        
        # VALIDACIÓN CRÍTICA: Fondos suficientes
        if cuenta.saldo < pago.monto:
            # CANCELAR pago según tu flujo
            pago.estado = 'CANCELADO'
            pago.notas = f'Fondos insuficientes. Saldo: ${cuenta.saldo}, Requerido: ${pago.monto}'
            
            # Liberar gasto asociado (vuelve a APROBADO)
            gasto = Gasto.query.get(pago.gasto_id)
            gasto.estado = 'APROBADO'
            
            db.session.commit()
            return False, 'Fondos insuficientes. Pago cancelado. Debe generar nuevo pago con cuenta diferente.'
        
        # EJECUTAR PAGO (fondos suficientes)
        try:
            # 1. Restar del saldo de la cuenta
            cuenta.saldo -= pago.monto
            
            # 2. Actualizar estado del pago
            pago.estado = 'EJECUTADO'
            pago.fecha_ejecucion = datetime.utcnow()
            pago.notas = 'Pago ejecutado exitosamente'
            
            # 3. Actualizar estado del gasto
            gasto = Gasto.query.get(pago.gasto_id)
            gasto.estado = 'PAGADO'
            
            db.session.commit()
            return True, 'Pago ejecutado exitosamente'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al ejecutar pago: {str(e)}'
    
    @staticmethod
    def cancelar_pago(pago_id, motivo=None):
        """Cancela un pago y libera el gasto asociado"""
        pago = Pago.query.get_or_404(pago_id)
        
        if pago.estado in ['EJECUTADO', 'CANCELADO']:
            return False, f"No se puede cancelar un pago en estado {pago.estado}"
        
        try:
            # 1. Actualizar estado del pago
            pago.estado = 'CANCELADO'
            pago.notas = motivo or 'Cancelado por el usuario'
            
            # 2. Liberar gasto asociado (vuelve a APROBADO según tu flujo)
            gasto = Gasto.query.get(pago.gasto_id)
            gasto.estado = 'APROBADO'
            
            db.session.commit()
            return True, 'Pago cancelado exitosamente'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al cancelar pago: {str(e)}'
    
    @staticmethod
    def aprobar_pago(pago_id):
        """Aprueba un pago pendiente"""
        pago = Pago.query.get_or_404(pago_id)
        
        if pago.estado != 'PENDIENTE':
            return False, f"El pago está en estado {pago.estado}, debe estar PENDIENTE"
        
        try:
            pago.estado = 'APROBADO'
            db.session.commit()
            return True, 'Pago aprobado exitosamente'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al aprobar pago: {str(e)}'
    
    @staticmethod
    def obtener_pagos_por_cuenta(cuenta_id):
        """Obtiene todos los pagos de una cuenta con estadísticas"""
        cuenta = CuentaBancaria.query.get_or_404(cuenta_id)
        
        pagos = Pago.query.filter_by(cuenta_id=cuenta_id).all()
        
        # Calcular estadísticas
        total_ejecutado = sum(p.monto for p in pagos if p.estado == 'EJECUTADO')
        total_pendiente = sum(p.monto for p in pagos if p.estado in ['PENDIENTE', 'APROBADO'])
        
        return {
            'cuenta': cuenta,
            'pagos': pagos,
            'estadisticas': {
                'total_ejecutado': total_ejecutado,
                'total_pendiente': total_pendiente,
                'saldo_disponible': cuenta.saldo,
                'saldo_tras_pagos_pendientes': cuenta.saldo - total_pendiente
            }
        }
    
    @staticmethod
    def cambiar_cuenta_pago(pago_id, nueva_cuenta_id):
        """Cambia la cuenta de un pago pendiente"""
        pago = Pago.query.get_or_404(pago_id)
        
        if pago.estado != 'PENDIENTE':
            return False, "Solo se puede cambiar cuenta de pagos PENDIENTES"
        
        nueva_cuenta = CuentaBancaria.query.get_or_404(nueva_cuenta_id)
        
        try:
            # Guardar historial del cambio
            cuenta_anterior = CuentaBancaria.query.get(pago.cuenta_id)
            
            pago.cuenta_id = nueva_cuenta_id
            pago.notas = f"Cuenta cambiada de {cuenta_anterior.nombre_cuenta} a {nueva_cuenta.nombre_cuenta}"
            
            db.session.commit()
            return True, 'Cuenta cambiada exitosamente'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Error al cambiar cuenta: {str(e)}'