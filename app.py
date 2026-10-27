"""Dashboard Ejecutivo de Rendimiento Comercial y Logístico — Livingstones Global.

Stack: Python · SQLite3 · Pandas/NumPy · Plotly · Streamlit
Ejecutar:  streamlit run app.py
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ───────────────────────── Configuración ─────────────────────────
BASE = Path(__file__).parent
DB_PATH = BASE / "data" / "livingstones.db"

BLUE = "#00B3FF"        # azul neón
BLUE_DARK = "#1F4FFF"   # azul profundo (apoyo)
ORANGE = "#FF6B1A"      # naranja neón
BG = "#0A0E17"
TEXT = "#E6EDF7"
MUTED = "#7F8CA3"
GRID = "rgba(255,255,255,0.06)"

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
BANDAS = ["0% Sin Descuento", "1% - 10% Bajo", "11% - 20% Medio", "Más de 20% Alto"]

st.set_page_config(page_title="Livingstones Global · E-Commerce", layout="wide")

st.markdown(
    f"""
    <style>
      .block-container {{ padding-top: 2rem; max-width: 1400px; }}
      h1, h2, h3 {{ font-weight: 600; letter-spacing: -0.5px; }}
      .kicker {{ color: {BLUE}; font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; }}
      .sub {{ color: {MUTED}; margin-top: -0.6rem; margin-bottom: 1rem; }}
      /* Tarjetas KPI */
      [data-testid="stMetric"] {{
          background: #0F1524; border: 1px solid rgba(0,179,255,.35);
          border-radius: 10px; padding: 14px 18px;
          box-shadow: 0 0 14px rgba(0,179,255,.10);
      }}
      [data-testid="stMetricLabel"] p {{ color: {MUTED}; font-size: .85rem; }}
      [data-testid="stMetricValue"] {{ color: {TEXT}; font-size: 1.7rem; }}
      /* Contenedores de gráficos */
      [data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 10px; border-color: rgba(255,255,255,.08); }}
      .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
      .stTabs [aria-selected="true"] {{ color: {BLUE}; }}
      .stTabs [data-baseweb="tab-highlight"] {{ background-color: {ORANGE}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ───────────────────────── Capa de datos (SQLite) ─────────────────────────
@st.cache_data(show_spinner=False)
def load_orders() -> pd.DataFrame:
    if not DB_PATH.exists():
        st.error("No existe la base de datos. Ejecutá primero:  python etl.py")
        st.stop()
    with sqlite3.connect(DB_PATH) as con:
        df = pd.read_sql_query("SELECT * FROM v_orders", con, parse_dates=["order_date"])
    return df


df_all = load_orders()


# ───────────────────────── Utilidades ─────────────────────────
def es_num(x: float, dec: int = 2) -> str:
    """Formato es-AR: 1.234,56"""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def compacto(x: float) -> str:
    """5,11 M · 426 mil · 20 mil"""
    if abs(x) >= 1e6:
        return f"{es_num(x / 1e6)} M"
    if abs(x) >= 1e3:
        return f"{es_num(x / 1e3, 0)} mil"
    return es_num(x, 0)


def selector(label: str, opciones, key: str, fmt=None):
    return st.selectbox(label, ["Todas"] + list(opciones), key=key, format_func=fmt or str)


def style(fig: go.Figure, height: int = 380, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=legend,
        legend=dict(orientation="h", y=-0.15, font=dict(color=MUTED)),
        hoverlabel=dict(bgcolor="#111827", font_color=TEXT),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    return fig


def card_title(txt: str):
    st.markdown(f"**{txt}**")


def glow_line(color: str, width: int = 3) -> dict:
    return dict(color=color, width=width, shape="spline", smoothing=0.8)


# ───────────────────────── Encabezado ─────────────────────────
st.markdown('<div class="kicker">E-Commerce Analytics — Livingstones Global</div>', unsafe_allow_html=True)
st.title("Dashboard Ejecutivo de Rendimiento Comercial y Logístico")

tab1, tab2, tab3 = st.tabs(
    ["Desempeño Comercial", "Descuentos y Logística", "Clientes y Medios de Pago"]
)

# ═════════════════════════ PÁGINA 1 · Desempeño Comercial ═════════════════════════
with tab1:
    h, f1, f2 = st.columns([4, 1, 1])
    with h:
        st.header("Desempeño Comercial y Distribución Regional")
        st.markdown('<div class="sub">Análisis de la evolución temporal de ventas y rendimiento geográfico.</div>', unsafe_allow_html=True)
    with f1:
        anio = selector("Año", sorted(df_all["anio"].unique()), "p1_anio")
    with f2:
        mes = selector("Mes", range(1, 13), "p1_mes", fmt=lambda m: m if m == "Todas" else MESES[m - 1])

    d = df_all.copy()
    if anio != "Todas":
        d = d[d["anio"] == anio]
    if mes != "Todas":
        d = d[d["mes"] == mes]

    k = st.columns(5)
    k[0].metric("Total facturado", compacto(d["revenue"].sum()))
    k[1].metric("Total pedidos", es_num(d["order_id"].nunique(), 0))
    k[2].metric("Total unidades", es_num(d["quantity"].sum(), 0))
    k[3].metric("Ticket promedio", f"$ {es_num(d['revenue'].mean())}")
    k[4].metric("Ticket mediano", f"$ {es_num(d['revenue'].median())}")

    left, right = st.columns([1, 1])

    with left:
        with st.container(border=True):
            card_title("Total facturado por Mes")
            m = d.groupby("mes", as_index=False)["revenue"].sum().sort_values("mes")
            m["mes_txt"] = m["mes"].map(lambda i: MESES[i - 1])
            fig = go.Figure(
                go.Scatter(
                    x=m["mes_txt"], y=m["revenue"], mode="lines+markers+text",
                    line=glow_line(BLUE), marker=dict(size=8, color=BLUE),
                    fill="tozeroy", fillcolor="rgba(0,179,255,0.12)",
                    text=[compacto(v) for v in m["revenue"]], textposition="top center",
                    textfont=dict(color=MUTED, size=11),
                    hovertemplate="%{x}: $ %{y:,.0f}<extra></extra>",
                )
            )
            lo, hi = m["revenue"].min(), m["revenue"].max()
            pad = (hi - lo) * 0.15 or hi * 0.05
            fig.update_yaxes(range=[lo - pad * 2, hi + pad], tickformat=".2s")
            fig.update_xaxes(categoryorder="array", categoryarray=MESES)
            st.plotly_chart(style(fig, 640, legend=False), width="stretch")

    with right:
        with st.container(border=True):
            card_title("Distribución de Ventas y Caza de Outliers por Categoría")
            fig = go.Figure()
            for cat in sorted(d["product_category"].unique()):
                fig.add_trace(
                    go.Box(
                        y=d.loc[d["product_category"] == cat, "revenue"], name=cat,
                        boxpoints="outliers", boxmean=True,
                        line=dict(color=BLUE, width=1.5), fillcolor="rgba(0,179,255,0.15)",
                        marker=dict(color=ORANGE, size=5, opacity=0.8),
                        marker_outliercolor=ORANGE,
                        hovertemplate="$ %{y:,.0f}<extra>" + cat + "</extra>",
                    )
                )
            fig.update_yaxes(title="Facturación por pedido ($)")
            st.plotly_chart(style(fig, 300, legend=False), width="stretch")

        with st.container(border=True):
            card_title("Total facturado por región")
            r = d.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue")
            fig = go.Figure(
                go.Bar(
                    x=r["revenue"], y=r["region"], orientation="h",
                    marker=dict(color=ORANGE), text=[compacto(v) for v in r["revenue"]],
                    textposition="outside", textfont=dict(color=MUTED),
                    hovertemplate="%{y}: $ %{x:,.0f}<extra></extra>",
                )
            )
            fig.update_xaxes(range=[0, r["revenue"].max() * 1.2], tickformat=".2s")
            st.plotly_chart(style(fig, 270, legend=False), width="stretch")

# ═════════════════════════ PÁGINA 2 · Descuentos y Logística ═════════════════════════
with tab2:
    h, f1, f2 = st.columns([4, 1, 1])
    with h:
        st.header("Análisis de Descuentos y Operaciones Logísticas")
    with f1:
        cat = selector("Categoría", sorted(df_all["product_category"].unique()), "p2_cat")
    with f2:
        reg = selector("Región", sorted(df_all["region"].unique()), "p2_reg")

    d = df_all.copy()
    if cat != "Todas":
        d = d[d["product_category"] == cat]
    if reg != "Todas":
        d = d[d["region"] == reg]

    n_ped = d["order_id"].nunique()
    k = st.columns(4)
    k[0].metric("Unidades por pedido", es_num(d["quantity"].sum() / n_ped if n_ped else 0))
    k[1].metric("Total pedidos", es_num(n_ped, 0))
    k[2].metric("Días de entrega promedio", es_num(d["delivery_days"].mean()))
    k[3].metric("Satisfacción cliente (1-5)", es_num(d["customer_rating"].mean()))

    g = (
        d.groupby("banda_descuento")
        .agg(facturado=("revenue", "sum"), pedidos=("order_id", "nunique"), unidades=("quantity", "sum"))
        .reindex(BANDAS)
        .fillna(0)
        .reset_index()
    )
    g["uxp"] = np.where(g["pedidos"] > 0, g["unidades"] / g["pedidos"], np.nan)

    left, right = st.columns([1, 1])

    with left:
        with st.container(border=True):
            card_title("Satisfacción del Cliente según Días de Entrega")
            s = d.groupby("delivery_days", as_index=False)["customer_rating"].mean().sort_values("delivery_days")
            fig = go.Figure(
                go.Bar(
                    x=s["customer_rating"], y=s["delivery_days"].astype(str) + " d", orientation="h",
                    marker=dict(color=BLUE), text=[es_num(v) for v in s["customer_rating"]],
                    textposition="outside", textfont=dict(color=MUTED),
                    hovertemplate="%{y}: %{x:.2f}<extra></extra>",
                )
            )
            fig.update_xaxes(range=[0, 5], title="Satisfacción promedio (escala 1-5)")
            fig.update_yaxes(autorange="reversed", type="category")
            st.plotly_chart(style(fig, 600, legend=False), width="stretch")

    with right:
        with st.container(border=True):
            card_title("Impacto de Descuentos en Facturación y Unidades por Pedido")
            fig = go.Figure()
            fig.add_bar(x=g["banda_descuento"], y=g["facturado"], name="Total facturado",
                        marker_color=BLUE, hovertemplate="$ %{y:,.0f}<extra>Facturado</extra>")
            fig.add_scatter(x=g["banda_descuento"], y=g["uxp"], name="Unidades por pedido",
                            yaxis="y2", mode="lines+markers", line=glow_line(ORANGE),
                            marker=dict(size=8, color=ORANGE),
                            hovertemplate="%{y:.2f}<extra>Unid./pedido</extra>")
            lo, hi = g["uxp"].min(), g["uxp"].max()
            fig.update_layout(
                yaxis=dict(tickformat=".2s", title="Facturado ($)"),
                yaxis2=dict(overlaying="y", side="right", showgrid=False, title="Unid./pedido",
                            range=[lo - 0.02, hi + 0.02] if pd.notna(lo) else None),
            )
            st.plotly_chart(style(fig, 290), width="stretch")

        with st.container(border=True):
            card_title("Volumen de Facturación y Unidades Totales por Descuento")
            fig = go.Figure()
            fig.add_bar(x=g["banda_descuento"], y=g["facturado"], name="Total facturado",
                        marker_color=BLUE, hovertemplate="$ %{y:,.0f}<extra>Facturado</extra>")
            fig.add_scatter(x=g["banda_descuento"], y=g["unidades"], name="Total unidades",
                            yaxis="y2", mode="lines+markers", line=glow_line(ORANGE),
                            marker=dict(size=8, color=ORANGE),
                            hovertemplate="%{y:,.0f}<extra>Unidades</extra>")
            fig.update_layout(
                yaxis=dict(tickformat=".2s", title="Facturado ($)"),
                yaxis2=dict(overlaying="y", side="right", showgrid=False, title="Unidades", rangemode="tozero"),
            )
            st.plotly_chart(style(fig, 290), width="stretch")

# ═════════════════════════ PÁGINA 3 · Clientes y Medios de Pago ═════════════════════════
with tab3:
    st.header("Clientes y Medios de Pago")
    f1, f2, _ = st.columns([1, 1, 4])
    with f1:
        reg = selector("Región", sorted(df_all["region"].unique()), "p3_reg")
    with f2:
        anio = selector("Año", sorted(df_all["anio"].unique()), "p3_anio")

    d = df_all.copy()
    if reg != "Todas":
        d = d[d["region"] == reg]
    if anio != "Todas":
        d = d[d["anio"] == anio]

    pedidos_cli = d.groupby("customer_id")["order_id"].nunique()
    n_unica = int((pedidos_cli == 1).sum())
    n_recur = int((pedidos_cli > 1).sum())
    pct_fact = d["revenue"].sum() / df_all["revenue"].sum() * 100

    k = st.columns(5)
    k[0].metric("Total clientes", es_num(len(pedidos_cli), 0))
    k[1].metric("Cliente compra única", es_num(n_unica, 0))
    k[2].metric("Clientes recurrentes", es_num(n_recur, 0))
    k[3].metric("% Facturación sobre total", f"{es_num(pct_fact, 0)} %")
    k[4].metric("Total facturado", compacto(d["revenue"].sum()))

    left, right = st.columns([1, 1])

    with left:
        with st.container(border=True):
            card_title("Distribución de Medios de Pago por Región")
            p = d.groupby(["region", "payment_method"]).size().unstack(fill_value=0)
            p = p.div(p.sum(axis=1), axis=0) * 100
            colores = {"Card": BLUE, "COD": BLUE_DARK, "Wallet": ORANGE}
            fig = go.Figure()
            for medio in [c for c in ["Card", "COD", "Wallet"] if c in p.columns]:
                fig.add_bar(
                    y=p.index, x=p[medio], name=medio, orientation="h", marker_color=colores[medio],
                    text=[f"{v:.0f}%" for v in p[medio]], textposition="inside",
                    hovertemplate="%{y} · " + medio + ": %{x:.1f}%<extra></extra>",
                )
            fig.update_layout(barmode="stack")
            fig.update_xaxes(range=[0, 100], ticksuffix="%")
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(style(fig, 460), width="stretch")

    with right:
        with st.container(border=True):
            card_title("Clientes únicos vs recurrentes")
            fig = go.Figure(
                go.Pie(
                    labels=["Clientes Recurrentes", "Cliente única compra"], values=[n_recur, n_unica],
                    hole=0.6, marker=dict(colors=[ORANGE, BLUE], line=dict(color=BG, width=3)),
                    textinfo="value+percent", textfont=dict(color="white"), sort=False,
                )
            )
            st.plotly_chart(style(fig, 460), width="stretch")
