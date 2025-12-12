# Gestión de Gastos y Pagos

## Requerimientos Funcionales

### Gestión del Ciclo de Vida del Gasto (Gastos)

2\. Requerimientos Funcionales (RF)
-----------------------------------

### RF1: Gestión del Ciclo de Vida del Gasto

El sistema debe permitir registrar gastos y gestionar sus estados.

- PENDIENTE: Estado inicial al crear un gasto. Datos requeridos: Monto, Concepto, Fecha Creación.
- APROBADO: El gasto ha sido validado por un supervisor. Listo para ser pagado.
- CANCELADO: El gasto se rechaza o anula. Es un estado final (no afecta balance).
- PAGADO: Estado automático asignado cuando el Gasto se vincula a un Pago EJECUTADO.

```mermaid
stateDiagram-v2
    direction LR
    
    %% Estados
    [*] --> PENDIENTE: Crear Gasto
    
    state "PENDIENTE DE APROBACIÓN" as PENDIENTE
    state "APROBADO" as APROBADO
    state "CANCELADO" as CANCELADO
    state "PAGADO" as PAGADO

    %% Transiciones
    PENDIENTE --> APROBADO: Aprobar
    PENDIENTE --> CANCELADO: Cancelar
    
    APROBADO --> CANCELADO: Cancelar
    APROBADO --> PAGADO: Vincular Pago (Ejecutado)
    
    %% Finales
    CANCELADO --> [*]
    PAGADO --> [*]
    
    note right of PAGADO
       Estado final automático
       cuando el Pago se ejecuta.
    end note
    

```
### RF2: Gestión del Ciclo de Vida del Pago

El sistema debe administrar la salida de dinero vinculada a gastos aprobados.

- PENDIENTE: El pago se ha generado pero no ha salido el dinero. Datos: Monto, Cuenta Origen, Fecha Prog.
- APROBADO: El pago está autorizado para dispersión.
- EJECUTADO: El dinero ha salido de la cuenta. Acción crítica: Debe restar el monto del Balance de la Cuenta Bancaria.
- CANCELADO: El proceso de pago se detiene. El Gasto asociado debe liberarse (volver a APROBADO).

```mermaid
stateDiagram-v2
    direction LR

    %% Estados
    [*] --> PENDIENTE: Generar desde Gasto
    
    state "PENDIENTE DE EJECUCIÓN" as PENDIENTE
    state "APROBADO" as APROBADO
    state "EJECUTADO" as EJECUTADO
    state "CANCELADO" as CANCELADO

    %% Transiciones
    PENDIENTE --> APROBADO: Autorizar
    PENDIENTE --> CANCELADO: Cancelar
    
    APROBADO --> EJECUTADO: Ejecutar Transferencia
    APROBADO --> CANCELADO: Cancelar
    
    %% Finales
    CANCELADO --> [*]
    EJECUTADO --> [*]

    note right of EJECUTADO
       Acción Crítica:
       Restar monto del Balance Bancario
       y cambiar estado del Gasto a PAGADO.
    end note
```
### RF3: Automatización (Vinculación)

*   **Generación Automática:** En la vista de un Gasto con estado **APROBADO**, debe existir un botón _"Generar Pago"_.
    
*   **Acción:** Al hacer clic, el sistema debe crear automáticamente un registro de Pago en estado **PENDIENTE** con el mismo monto del gasto seleccionado.
    

### RF4: Tesorería (Cuentas Bancarias)

*   **Catálogo de Cuentas:** Registro de cuentas (Ej. _Banco, No. Cuenta, Nombre_).
    
*   **Control de Saldos:**
    
    *   Cada cuenta tiene un **Balance Inicial**.
        
    *   El **Balance Actual** se calcula: Balance Inicial - Suma de Pagos EJECUTADOS.
        

### RF5: Dashboard y Reportes

La pantalla de inicio debe mostrar indicadores clave:

*   **Tablas:** Listado reciente de Gastos y Pagos con sus estados (con paginación o scroll).
    
*   **Gráficos:**
    
    *   Distribución de estatus de gastos (Pie chart o Barras).
        
    *   Balance total disponible en tesorería.
        

3\. Requerimientos No Funcionales (RNF)
---------------------------------------

*   **Backend:** Preferentemente **Python** (Flask o Django).
    
*   **Base de Datos:** Relacional (PostgreSQL, MySQL o SQLite).
    
*   **Frontend:** HTML5/CSS3. Se permite el uso de frameworks como Bootstrap o Tailwind para una interfaz limpia y profesional.
    
*   **Validaciones:** El sistema no debe permitir pagar un gasto que no esté aprobado, ni ejecutar un pago si la cuenta bancaria no tiene fondos suficientes (opcional, pero deseable).
