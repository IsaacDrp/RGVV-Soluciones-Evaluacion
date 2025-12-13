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
flowchart TD
    A[Inicio] --> B[Empleado crea nuevo gasto]
    B --> C[Llenar datos: Monto, Concepto, Solicitante]
    C --> D{Sistema valida datos?}
    D -->|No| E[Mostrar error<br>Corregir datos]
    E --> C
    D -->|Sí| F[Guardar gasto<br>Estado: PENDIENTE]
    F --> G[Mostrar mensaje éxito]
    G --> H{Supervisor revisa}
    
    H -->|Rechaza| I[Cancelar gasto]
    I --> J[Estado: CANCELADO]
    J --> K[Fin proceso]
    
    H -->|Aprueba| L[Aprobar gasto]
    L --> M[Estado: APROBADO]
    M --> N{Botón 'Generar Pago' presionado?}
    
    N -->|Sí| O[Sistema genera pago automático]
    O --> P[Crear registro de pago<br>Vinculado al gasto]
    P --> Q[Estado pago: PENDIENTE]
    Q --> R[Redirigir a vista de pagos]
    
    N -->|No| S[Esperar acción]
    S --> T{Acción posterior?}
    T -->|Editar| U[Permitir edición limitada]
    U --> M
    T -->|Cancelar| I
    T -->|Generar Pago| O

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style K fill:#f9f,stroke:#333,stroke-width:2px
    style J fill:#ff9999
    style M fill:#99ff99
    style F fill:#ffff99
```
### RF2: Gestión del Ciclo de Vida del Pago

El sistema debe administrar la salida de dinero vinculada a gastos aprobados.

- PENDIENTE: El pago se ha generado pero no ha salido el dinero. Datos: Monto, Cuenta Origen, Fecha Prog.
- EJECUTADO: El dinero ha salido de la cuenta. Acción crítica: Debe restar el monto del Balance de la Cuenta Bancaria.
- CANCELADO: El proceso de pago se detiene. El Gasto asociado debe liberarse (volver a APROBADO).

```mermaid
flowchart TD
    A[Inicio] --> B[Pago generado desde gasto aprobado]
    B --> C[Estado: PENDIENTE<br>Datos: Monto, Cuenta, Fecha Prog.]
    C --> D{Acción sobre pago?}
    
    D -->|Cancelar| E[Cancelar pago manualmente]
    E --> F[Estado: CANCELADO]
    F --> G[Liberar gasto asociado]
    G --> H[Gasto vuelve a estado APROBADO]
    H --> I[Fin proceso cancelado]
    
    D -->|Ejecutar| J[Intentar ejecutar transferencia]
    J --> K{Validar fondos en cuenta}
    
    K -->|SALDO INSUFICIENTE| L[Registrar error]
    L --> M[Estado: CANCELADO]
    M --> N[Liberar gasto asociado]
    N --> O[Gasto vuelve a APROBADO]
    O --> P[Notificar al usuario]
    P --> Q[Usuario debe generar NUEVO pago<br>con cuenta diferente]
    Q --> R[Fin - Requiere nuevo intento]
    
    K -->|FONDOS SUFICIENTES| S[Proceder con transferencia]
    S --> T[Restar monto del saldo de cuenta]
    T --> U[Actualizar saldo actual]
    U --> V[Estado: EJECUTADO]
    V --> W[Fecha ejecución = ahora]
    W --> X[Actualizar gasto asociado]
    X --> Y[Gasto: Estado PAGADO]
    Y --> Z[Fin proceso exitoso]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#ff9999,stroke:#333,stroke-width:2px
    style R fill:#ffcc99,stroke:#333,stroke-width:2px
    style Z fill:#99ff99,stroke:#333,stroke-width:2px
    style C fill:#ffff99
    style F fill:#ff9999
    style M fill:#ff9966
    style V fill:#99ff99
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
        string solicitante
        string concepto
        decimal monto
        datetime fecha_creacion
        string estado
        string motivo_cancelacion
    }

    PAGO {
        int id PK
        int gasto_id FK
        int cuenta_id FK
        decimal monto
        datetime fecha_creacion
        date fecha_programada
        datetime fecha_ejecucion
        string estado
        string motivo_cancelacion
        string notas
    }

    CUENTA_BANCARIA {
        int id PK
        string nombre_banco
        string nombre_cuenta
        string numero_cuenta UK
        decimal saldo
        string moneda
    }

    GASTO ||--o{ PAGO : genera
    CUENTA_BANCARIA ||--o{ PAGO : se_usa_en
```