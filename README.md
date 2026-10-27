# Livingstones Global · E-Commerce Analytics (Python)

Recreación en Python del dashboard de Power BI del proyecto de e-commerce
para la ONG Livingstones Global. Mismo análisis y los mismos KPIs, con un
stack 100% Python: **SQLite3 · Pandas/NumPy · Plotly · Streamlit**.

> ⚠️ **Nota sobre los datos:** el dataset es **sintético (dummy data)**,
> generado con fines de práctica y demostración técnica. No representa
> transacciones reales de Livingstones Global. Incluye fechas hasta 2035,
> conservadas intencionalmente como parte de la naturaleza sintética del
> dataset — ningún cálculo del dashboard usa la fecha actual del sistema.

---

## Estructura del proyecto

```
livingstones_dashboard/
├── app.py                  # Dashboard Streamlit (3 pestañas)
├── etl.py                  # ETL: CSV de staging → SQLite3
├── requirements.txt        # Dependencias
├── .streamlit/
│   └── config.toml         # Tema oscuro, azul y naranja neón
└── data/
    ├── stg_orders.csv      # Datos de staging (salida de la fase Excel/Power Query)
    └── livingstones.db     # Base SQLite3 generada por etl.py
```

## Cómo correrlo

**1. Instalar dependencias** (se recomienda un entorno virtual):
```bash
pip install -r requirements.txt
```

**2. Generar la base de datos**, a partir de `data/stg_orders.csv`:
```bash
python etl.py
```
Esto crea `data/livingstones.db` con la tabla `orders` (datos limpios y
tipados) y la vista `v_orders` (agrega año, mes y banda de descuento).
El ETL valida que `revenue` sea consistente con
`quantity × unit_price × (1 − discount)`; si encuentra desvíos superiores
a 0,05 en algún registro, lo avisa por consola.

**3. Levantar el dashboard:**
```bash
streamlit run app.py
```
Si `data/livingstones.db` no existe todavía, la app lo indica en pantalla
y pide correr `etl.py` primero.

## Estructura del dashboard (3 pestañas)

**1. Desempeño Comercial y Distribución Regional**
Evolución temporal de ventas y rendimiento geográfico. KPIs: Total
facturado, Total pedidos, Total unidades, Ticket promedio, Ticket
mediano. Incluye el diagnóstico estadístico de media vs. mediana y la
distribución de outliers por categoría.

**2. Descuentos y Logística**
Impacto de las bandas de descuento (Sin descuento, 1%-10%, 11%-20%,
Más de 20%) sobre facturación y unidades, y desempeño de entrega. KPIs:
Unidades por pedido, Total pedidos, Días de entrega promedio,
Satisfacción del cliente (1-5).

**3. Clientes y Medios de Pago**
Distribución de clientes únicos vs. recurrentes y ventas por medio de
pago. KPIs: Total clientes, Cliente compra única, Clientes recurrentes,
% Facturación sobre total, Total facturado.

Cada pestaña tiene sus propios filtros (año, región, categoría según la
pestaña) mediante selectores independientes.

## Estilo visual

Tema oscuro minimalista, definido en `.streamlit/config.toml` y reforzado
con CSS embebido en `app.py`:

| Elemento | Color |
|---|---|
| Azul neón (acento principal) | `#00B3FF` |
| Azul profundo (apoyo) | `#1F4FFF` |
| Naranja neón (acento secundario) | `#FF6B1A` |
| Fondo | `#0A0E17` |
| Texto | `#E6EDF7` |

## Origen de los datos

`data/stg_orders.csv` es la salida de la fase de limpieza y validación
hecha en Excel/Power Query (consulta `stg_orders`) durante la primera
etapa del proyecto, antes de migrar el modelo a SQL Server para el
dashboard original en Power BI. Esta versión en Python parte de ese mismo
CSV validado, sin pasar por SQL Server.

## Limitación conocida

Al igual que en la versión de Power BI, el dataset registra **facturación
(`revenue`)** pero no costo por producto: el análisis mide ingresos
brutos, no rentabilidad real. Incorporar datos de costo queda como
posible paso siguiente.
