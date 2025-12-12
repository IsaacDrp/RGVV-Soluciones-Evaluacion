# Gestión de Gastos y Pagos

## Requerimientos Funcionales

### Gestión del Ciclo de Vida del Gasto (Gastos)

Requerimientos Funcionales (RF)
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

    %% Definición de Estados
    state "PENDIENTE (Borrador)" as PENDIENTE
    state "APROBADO (Por Tesorería)" as APROBADO
    state "EJECUTADO (Exitoso)" as EJECUTADO
    state "CANCELADO (Final)" as CANCELADO

    %% Nodo de decisión lógica (Backend)
    state validacion_fondos <<choice>>

    %% Inicio
    [*] --> PENDIENTE: Generar desde Gasto

    %% Ciclo de Aprobación
    PENDIENTE --> APROBADO: Autorizar Pago
    PENDIENTE --> CANCELADO: Descartar

    %% Intento de Ejecución
    APROBADO --> validacion_fondos: Ejecutar Transferencia

    %% LÓGICA DE VALIDACIÓN (El Core del Examen)
    
    %% Caso 1: Hay dinero -> Éxito
    validacion_fondos --> EJECUTADO: Si (Saldo >= Monto)
    
    %% Caso 2: No hay dinero -> Rebote (Loop)
    validacion_fondos --> PENDIENTE: No (Saldo Insuficiente)

    %% Cancelación desde Aprobado (Manual)
    APROBADO --> CANCELADO: Cancelar Manualmente

    %% Notas explicativas para el candidato
    note left of PENDIENTE
       Si falla la validación (Rebote),
       regresa aquí para que el usuario
       pueda corregir la cuenta bancaria.
    end note

    note right of EJECUTADO
       Solo se llega aquí si
       la validación de fondos
       fue exitosa.
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


# Diagrama Entidad Relación de la base de datos
```mermaid
erDiagram
    GASTO {
        int id PK
        string solicitante "Nombre del empleado"
        string concepto "Descripcion"
        decimal monto "Total a pagar"
        datetime fecha_creacion
        enum estado "PENDIENTE, APROBADO, CANCELADO, PAGADO"
    }

    PAGO {
        int id PK
        int gasto_id FK "Relacion 1:1"
        int cuenta_id FK "Cuenta seleccionada para pagar"
        decimal monto "Monto a transferir"
        date fecha_ejecucion "Se llena solo al EJECUTAR"
        enum estado "PENDIENTE, APROBADO, EJECUTADO, CANCELADO"
        string notas "Explica el fallo (Ej. Fondos insuficientes)"
    }

    CUENTA_BANCARIA {
        int id PK
        string nombre_banco "Ej. Santander"
        string numero_cuenta
        decimal saldo_actual "Se valida contra PAGO.monto"
        string moneda "MXN/USD (Opcional)"
    }

    %% Relaciones
    GASTO ||--o| PAGO : "origina"
    CUENTA_BANCARIA ||--o{ PAGO : "financia"
```