# app.py
import streamlit as st
import matplotlib.pyplot as plt
from fews_core import obtener_datos, estado_actual, ALERTA_ROJA, ALERTA_NARANJA

# ================= CONFIG STREAMLIT =================
st.set_page_config(
    page_title="Monitor Río Sinú – Montería",
    layout="wide"
)

# ================= TEMA =================
if "tema" not in st.session_state:
    st.session_state.tema = "oscuro"

def es_oscuro():
    return st.session_state.tema == "oscuro"

# ================= COLORES POR TEMA =================
if es_oscuro():
    FONDO = "#0e1117"
    TEXTO = "white"
    CARD = "#1c1f26"
    GRID = "#333"
    BORDE = "#444"
    LINEA_NIVEL = "#4da3ff"
    LINEA_VEL = "#c77dff"
    BARRA_LLUVIA = "#4cc9f0"
    BTN_BG = "#2563eb"     # azul
    BTN_HOVER = "#1d4ed8"
    BTN_TEXT = "white"
else:
    FONDO = "#ffffff"
    TEXTO = "#111111"
    CARD = "#f5f5f5"
    GRID = "#dddddd"
    BORDE = "#aaaaaa"
    LINEA_NIVEL = "#1f77b4"
    LINEA_VEL = "#7b2cbf"
    BARRA_LLUVIA = "#1f77b4"
    BTN_BG = "#1f2937"     # gris oscuro
    BTN_HOVER = "#111827"
    BTN_TEXT = "white"


# ================= CSS DINÁMICO =================
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {FONDO};
            color: {TEXTO};
        }}
        div[data-testid="metric-container"] {{
            background-color: {CARD};
            border-radius: 10px;
            padding: 10px;
        }}

        div.stButton > button {{
            background-color: {BTN_BG};
            color: {BTN_TEXT};
            border-radius: 8px;
            height: 3em;
            font-weight: 600;
        }}
        div.stButton > button:hover {{
            background-color: {BTN_HOVER};
            color: {BTN_TEXT};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ================= FUNCION ESTILO GRAFICOS =================
def aplicar_estilo(ax, fig):
    fig.patch.set_facecolor(FONDO)
    ax.set_facecolor(FONDO)

    ax.xaxis.label.set_color(TEXTO)
    ax.yaxis.label.set_color(TEXTO)
    ax.tick_params(axis="x", colors=TEXTO)
    ax.tick_params(axis="y", colors=TEXTO)

    for spine in ax.spines.values():
        spine.set_color(BORDE)

    ax.grid(color=GRID, linestyle="--", linewidth=0.5, alpha=0.4)

# ================= HEADER =================
col_titulo, col_toggle = st.columns([6, 1])

with col_titulo:
    st.title("🌊 Monitor del Río Sinú – Montería")

with col_toggle:
    if st.button("☀️" if es_oscuro() else "🌙"):
        st.session_state.tema = "claro" if es_oscuro() else "oscuro"
        st.rerun()

if st.button("🔄 Actualizar datos"):
    st.rerun()

# ================= DATOS =================
df_nivel, df_pobs, fuente = obtener_datos()
estado = estado_actual(df_nivel)

# ================= INFO ACTUAL =================
st.subheader(
    f"📅 Datos actualizados: {df_nivel['fecha'].iloc[-1].strftime('%Y-%m-%d %H:%M')} "
    f"| Fuente: FEWS - IDEAM"
)

# ================= COLORES SEGÚN ESTADO =================
if es_oscuro():
    OK = "#22c55e"
    WARN = "#facc15"
    DANGER = "#ef4444"
else:
    OK = "#16a34a"
    WARN = "#ca8a04"
    DANGER = "#dc2626"

# Color para ESTADO
if "ROJA" in estado["alerta"]:
    COLOR_ESTADO = DANGER
    BTN_HOVER = "#b91c1c"
elif "NARANJA" in estado["alerta"]:
    COLOR_ESTADO = WARN
else:
    COLOR_ESTADO = OK

# Color para TENDENCIA
if "SUBIENDO" in estado["tendencia"]:
    COLOR_TENDENCIA = DANGER
elif "BAJANDO" in estado["tendencia"]:
    COLOR_TENDENCIA = OK
else:
    COLOR_TENDENCIA = WARN

# ================= INDICADORES =================
c1, c2, c3, c4 = st.columns(4)

c1.markdown(
    f"""
    <div style="
        background-color:{CARD};
        border-radius:10px;
        padding:16px;
        text-align:center;
        color:{TEXTO};
        font-weight:600;
        font-size:20px;
    ">
        Nivel (m)<br>{estado['nivel']:.2f}
    </div>
    """,
    unsafe_allow_html=True
)
c2.markdown(
    f"""
    <div style="
        background-color:{CARD};
        border-radius:10px;
        padding:16px;
        text-align:center;
        color:{TEXTO};
        font-weight:600;
        font-size:20px;
    ">
        Velocidad (m/h)<br>{estado['velocidad']:.3f}
    </div>
    """,
    unsafe_allow_html=True
)

c3.markdown(
    f"""
    <div style="
        background-color:{CARD};
        border-radius:10px;
        padding:16px;
        text-align:center;
        color:{COLOR_TENDENCIA};
        font-weight:600;
        font-size:20px;
    ">
        Tendencia<br>{estado['tendencia']}
    </div>
    """,
    unsafe_allow_html=True
)

c4.markdown(
    f"""
    <div style="
        background-color:{CARD};
        border-radius:10px;
        padding:16px;
        text-align:center;
        color:{COLOR_ESTADO};
        font-weight:700;
        font-size:20px;
    ">
        Estado<br>{estado['alerta']}
    </div>
    """,
    unsafe_allow_html=True
)

# ================= GRÁFICO NIVEL =================
st.subheader("📈 Nivel del río")

fig, ax = plt.subplots()

ax.plot(
    df_nivel["fecha"],
    df_nivel["nivel"],
    label="Nivel del río",
    linewidth=2,
    color=LINEA_NIVEL
)

ax.axhline(ALERTA_ROJA, linestyle="--", color="red", label="Alerta Roja")
ax.axhline(ALERTA_NARANJA, linestyle="--", color="orange", label="Alerta Naranja")

ultimo = df_nivel.iloc[-1]
ax.annotate(
    f"Último: {ultimo['nivel']:.2f} m",
    xy=(ultimo["fecha"], ultimo["nivel"]),
    xytext=(10, 10),
    textcoords="offset points",
    arrowprops=dict(arrowstyle="->", color=TEXTO),
    fontsize=9,
    color=TEXTO,
    bbox=dict(boxstyle="round,pad=0.3", fc=CARD, ec=BORDE)
)

ax.set_ylabel("Nivel (m)")
ax.set_xlabel("Fecha")
ax.legend(facecolor=CARD, edgecolor=BORDE, labelcolor=TEXTO)

plt.xticks(rotation=45)
aplicar_estilo(ax, fig)
fig.tight_layout()
st.pyplot(fig)

# ================= GRÁFICO VELOCIDAD =================
st.subheader("⚡ Velocidad de cambio")

fig2, ax2 = plt.subplots()

ax2.plot(
    df_nivel["fecha"],
    df_nivel["vel_m_h"],
    label="Velocidad (m/h)",
    linewidth=2,
    color=LINEA_VEL
)

ax2.axhline(0, linestyle="--", color="gray", label="Nivel estable")

ultimo_v = df_nivel.iloc[-1]
ax2.annotate(
    f"{ultimo_v['vel_m_h']:.3f} m/h",
    xy=(ultimo_v["fecha"], ultimo_v["vel_m_h"]),
    xytext=(10, 10),
    textcoords="offset points",
    arrowprops=dict(arrowstyle="->", color=TEXTO),
    fontsize=9,
    color=TEXTO,
    bbox=dict(boxstyle="round,pad=0.3", fc=CARD, ec=BORDE)
)

ax2.set_ylabel("m/h")
ax2.set_xlabel("Fecha")
ax2.legend(facecolor=CARD, edgecolor=BORDE, labelcolor=TEXTO)

plt.xticks(rotation=45)
aplicar_estilo(ax2, fig2)
fig2.tight_layout()
st.pyplot(fig2)

# ================= GRÁFICO LLUVIA =================
st.subheader("🌧️ Precipitación")

fig3, ax3 = plt.subplots()

ax3.bar(
    df_pobs["fecha"],
    df_pobs["Pobs"],
    label="Precipitación diaria",
    color=BARRA_LLUVIA
)

if not df_pobs.empty:
    ult_lluvia = df_pobs.iloc[-1]
    ax3.annotate(
        f"{ult_lluvia['Pobs']:.1f} mm",
        xy=(ult_lluvia["fecha"], ult_lluvia["Pobs"]),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        color=TEXTO,
        bbox=dict(boxstyle="round,pad=0.3", fc=CARD, ec=BORDE)
    )

ax3.set_ylabel("mm")
ax3.set_xlabel("Fecha")
ax3.legend(facecolor=CARD, edgecolor=BORDE, labelcolor=TEXTO)

plt.xticks(rotation=45)
aplicar_estilo(ax3, fig3)
fig3.tight_layout()
st.pyplot(fig3)
