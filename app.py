from datetime import datetime
import io
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS UNIFICADOS (ESTILO REVALORIZA) ---
st.set_page_config(
    page_title="Gestión Flipping Multi-Proyecto",
    layout="wide"
)

# Mantener la app activa evitando que Streamlit Cloud la duerma por inactividad (refresco cada 10 min)
st_autorefresh(interval=600000, limit=None, key="keepalive_counter")

st.markdown("""  
<style>
/* Títulos principales con tono elegante */  
h1 {  
    font-size: 26px !important;  
    font-weight: 700 !important;  
    color: #1a202c !important;  
    margin-bottom: 0.8rem !important;  
}  

/* Títulos de pestañas y secciones principales */  
h2 {  
    font-size: 20px !important;  
    font-weight: 600 !important;  
    color: #2d3748 !important;  
    margin-top: 1.2rem !important;  
    margin-bottom: 0.6rem !important;  
}  

/* Títulos internos de tablas o reportes */  
h3 {  
    font-size: 16px !important;  
    font-weight: 600 !important;  
    color: #4a5568 !important;  
    margin-top: 1rem !important;  
    margin-bottom: 0.4rem !important;  
}  

/* UNIFICACIÓN VISUAL: Títulos/Etiquetas de campos en formularios y filtros */  
.field-title {  
    color: #3182ce !important;  
    font-weight: 400 !important;  
    font-size: 13px !important;  
    text-transform: uppercase !important;  
    letter-spacing: 0.5px !important;  
    margin-bottom: 4px;  
}  

/* Tarjetas de Métricas Personalizadas estilo Revaloriza */  
.metric-card {  
    background-color: #f8fafc;  
    border: 1px solid #e2e8f0;  
    border-radius: 8px;  
    padding: 16px 20px;  
    margin-bottom: 10px;  
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);  
}  

.metric-label {  
    font-size: 13px;  
    color: #718096;  
    font-weight: 500;  
    margin-bottom: 4px;  
}  

.metric-value {  
    font-size: 18px;  
    color: #1a202c;  
    font-weight: 600;  
}  

/* UNIFICACIÓN GLOBAL DE TABLAS (Desktop) */  
table th {  
    font-size: 13px !important;  
    text-transform: uppercase !important;  
    letter-spacing: 0.5px !important;  
    font-weight: 400 !important;  
    color: #2b6cb0 !important;  
    background-color: #ebf8ff !important;  
    white-space: nowrap !important;  
}  

table td {  
    white-space: nowrap !important;  
    padding-top: 10px !important;  
    padding-bottom: 10px !important;  
    color: #2d3748 !important;  
}  

/* ========================================== */
/* ADAPTACIÓN RESPONSIVE PARA CELULARES       */
/* ========================================== */
@media (max-width: 768px) {
    table th, table td {
        white-space: normal !important;  
        font-size: 11px !important;
        padding: 8px 6px !important;
    }
    h1 { font-size: 22px !important; }
    h2 { font-size: 17px !important; }
    h3 { font-size: 14px !important; }
    .metric-card {
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .metric-value {  
        font-size: 15px !important;  
    }
}
</style>  
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE LA BASE DE DATOS SQLITE ---
DB_NAME = "flipping_multiproyecto.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            cliente TEXT,
            superficie_total REAL,
            precio_compra INTEGER,
            presupuesto_reforma INTEGER,
            precio_objetivo INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            rubro_principal TEXT,
            contacto TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rubros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ambientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medios_pago (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            tipo TEXT,
            detalle TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presupuestos_rubro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            rubro TEXT,
            ambiente TEXT,
            proveedor TEXT,
            concepto TEXT,
            moneda TEXT,
            monto_presupuestado INTEGER,
            FOREIGN KEY(proyecto_id) REFERENCES proyectos(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            presupuesto_id INTEGER,
            fecha TEXT,
            comprobante TEXT,
            tipo_gasto TEXT,
            medio_pago TEXT,
            cuotas INTEGER,
            rubro TEXT,
            ambiente TEXT,
            proveedor TEXT,
            concepto TEXT,
            monto_ars INTEGER,
            tipo_cambio INTEGER,
            monto_usd INTEGER,
            FOREIGN KEY(proyecto_id) REFERENCES proyectos(id),
            FOREIGN KEY(presupuesto_id) REFERENCES presupuestos_rubro(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS especificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            pago_id INTEGER,
            rubro TEXT,
            ambiente TEXT,
            proveedor TEXT,
            producto_concepto TEXT,
            detalles_tecnicos TEXT,
            FOREIGN KEY(proyecto_id) REFERENCES proyectos(id),
            FOREIGN KEY(pago_id) REFERENCES pagos(id)
        )
    """)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM proyectos")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO proyectos (id, nombre, cliente, superficie_total, precio_compra, presupuesto_reforma, precio_objetivo) 
            VALUES (1, 'Coronel Díaz 2109 5° A', 'Verona', 137, 350000, 90000, 580000)
        """)
        conn.commit()
        
    cursor.execute("SELECT COUNT(*) FROM rubros")
    if cursor.fetchone()[0] == 0:
        rubros_iniciales = [
            "Demolición y Albañilería",
            "Instalaciones (Termomecánica/Sanitarios)",
            "Electricidad y Domótica",
            "Carpintería A30 y Puertas",
            "Pisos y Revestimientos",
            "Amoblamientos de Cocina y Placards",
        ]
        for r in rubros_iniciales:
            cursor.execute("INSERT OR IGNORE INTO rubros (nombre) VALUES (?)", (r,))
        conn.commit()

    cursor.execute("SELECT COUNT(*) FROM ambientes")
    if cursor.fetchone()[0] == 0:
        ambientes_iniciales = [
            "Cocina",
            "Baño 1",
            "Baño 2",
            "Toilette",
            "Living y Pasillos",
            "Balcón",
            "General"
        ]
        for a in ambientes_iniciales:
            cursor.execute("INSERT OR IGNORE INTO ambientes (nombre) VALUES (?)", (a,))
        conn.commit()
        
    cursor.execute("SELECT COUNT(*) FROM proveedores")
    if cursor.fetchone()[0] == 0:
        prov_iniciales = [
            ("SBG", "Pisos y Revestimientos", "Local Comercial"),
            ("Egger", "Amoblamientos", "Fábrica"),
            ("Aluar", "Aberturas", "Distribuidor"),
        ]
        for p, r, c in prov_iniciales:
            cursor.execute("INSERT OR IGNORE INTO proveedores (nombre, rubro_principal, contacto) VALUES (?, ?, ?)", (p, r, c))
        conn.commit()
        
    cursor.execute("SELECT COUNT(*) FROM medios_pago")
    if cursor.fetchone()[0] == 0:
        medios_iniciales = [
            ("Efectivo USD", "Efectivo", "Caja fuerte"),
            ("Transferencia Banco Galicia", "Transferencia", "Cuenta Corriente ARS"),
            ("Visa Galicia (Principal)", "Tarjeta de Crédito", "Cierre día 20"),
            ("Mastercard BBVA", "Tarjeta de Crédito", "Cierre día 15"),
            ("Cheque propio", "Cheque", "Banco Galicia"),
        ]
        for m, t, d in medios_iniciales:
            cursor.execute("INSERT OR IGNORE INTO medios_pago (nombre, tipo, detalle) VALUES (?, ?, ?)", (m, t, d))
        conn.commit()
        
    conn.close()

init_db()

# --- CONTROL DE ACCESO (LOGIN POR CONTRASEÑA) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.perfil = None

if not st.session_state.authenticated:
    st.title("🔐 Acceso Restringido - Gestión Flipping")
    st.markdown("Por favor, ingresá tu contraseña para acceder al sistema.")
    
    with st.form("login_form"):
        password_input = st.text_input("Contraseña", type="password")
        submit_login = st.form_submit_button("Ingresar")
        
        if submit_login:
            try:
                admin_pass = st.secrets["auth"]["admin_password"]
                client_pass = st.secrets["auth"]["client_password"]
            except:
                admin_pass = "admin2026"
                client_pass = "cliente2026"
                
            if password_input == admin_pass:
                st.session_state.authenticated = True
                st.session_state.perfil = "Project Manager (Admin)"
                st.success("¡Acceso concedido como Administrador!")
                st.rerun()
            elif password_input == client_pass:
                st.session_state.authenticated = True
                st.session_state.perfil = "Inversora / Cliente"
                st.success("¡Acceso concedido como Cliente!")
                st.rerun()
            else:
                st.error("Contraseña incorrecta. Verificá los datos.")
    st.stop()

perfil = st.session_state.perfil

# --- FUNCIONES DE BASE DE DATOS ---
def get_proyectos():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM proyectos", conn)
    conn.close()
    return df

def get_proveedores():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM proveedores", conn)
    conn.close()
    return df["nombre"].tolist()

def get_proveedores_df():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM proveedores", conn)
    conn.close()
    return df

def get_rubros():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM rubros", conn)
    conn.close()
    return df["nombre"].tolist()

def get_rubros_df():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM rubros", conn)
    conn.close()
    return df

def get_ambientes():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM ambientes", conn)
    conn.close()
    return df["nombre"].tolist()

def get_ambientes_df():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM ambientes", conn)
    conn.close()
    return df

def get_medios_pago():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM medios_pago", conn)
    conn.close()
    return df["nombre"].tolist()

def get_medios_pago_df():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM medios_pago", conn)
    conn.close()
    return df

def get_pagos(proyecto_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM pagos WHERE proyecto_id = ?", conn, params=(proyecto_id,))
    conn.close()
    return df

def agregar_pago(proyecto_id, presupuesto_id, fecha, comprobante, tipo_gasto, medio_pago, cuotas, rubro, ambiente, proveedor, concepto, monto_ars, tipo_cambio):
    monto_usd = int(monto_ars / tipo_cambio) if tipo_cambio > 0 else 0
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("INSERT OR IGNORE INTO rubros (nombre) VALUES (?)", (rubro,))
    cursor.execute("INSERT OR IGNORE INTO ambientes (nombre) VALUES (?)", (ambiente,))
    
    cursor.execute("""
        INSERT INTO pagos (proyecto_id, presupuesto_id, fecha, comprobante, tipo_gasto, medio_pago, cuotas, rubro, ambiente, proveedor, concepto, monto_ars, tipo_cambio, monto_usd) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (proyecto_id, presupuesto_id, fecha, comprobante, tipo_gasto, medio_pago, int(cuotas), rubro, ambiente, proveedor, concepto, int(monto_ars), int(tipo_cambio), int(monto_usd)))
    pago_id = cursor.lastrowid
    
    if tipo_gasto == "Material / Producto":
        cursor.execute("""
            INSERT INTO especificaciones (proyecto_id, pago_id, rubro, ambiente, proveedor, producto_concepto, detalles_tecnicos) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (proyecto_id, pago_id, rubro, ambiente, proveedor, concepto, "Pendiente de detalle técnico..."))
        
    conn.commit()
    conn.close()

def eliminar_pago(pago_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM especificaciones WHERE pago_id = ?", (pago_id,))
    cursor.execute("DELETE FROM pagos WHERE id = ?", (pago_id,))
    conn.commit()
    conn.close()

def eliminar_todos_los_pagos(proyecto_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM especificaciones WHERE proyecto_id = ?", (proyecto_id,))
    cursor.execute("DELETE FROM pagos WHERE proyecto_id = ?", (proyecto_id,))
    conn.commit()
    conn.close()

def actualizar_pago_completo(pago_id, presupuesto_id, fecha, comprobante, tipo_gasto, medio_pago, cuotas, rubro, ambiente, proveedor, concepto, monto_ars, tipo_cambio):
    monto_usd = int(monto_ars / tipo_cambio) if tipo_cambio > 0 else 0
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("INSERT OR IGNORE INTO rubros (nombre) VALUES (?)", (rubro,))
    cursor.execute("INSERT OR IGNORE INTO ambientes (nombre) VALUES (?)", (ambiente,))
    
    cursor.execute("""
        UPDATE pagos SET presupuesto_id = ?, fecha = ?, comprobante = ?, tipo_gasto = ?, medio_pago = ?, cuotas = ?, rubro = ?, ambiente = ?, proveedor = ?, concepto = ?, monto_ars = ?, tipo_cambio = ?, monto_usd = ? 
        WHERE id = ?
    """, (presupuesto_id, fecha, comprobante, tipo_gasto, medio_pago, int(cuotas), rubro, ambiente, proveedor, concepto, int(monto_ars), int(tipo_cambio), int(monto_usd), pago_id))
    
    cursor.execute("SELECT detalles_tecnicos FROM especificaciones WHERE pago_id = ?", (pago_id,))
    row_esp = cursor.fetchone()
    detalles_previos = row_esp[0] if row_esp else "Pendiente de detalle técnico..."
    
    cursor.execute("DELETE FROM especificaciones WHERE pago_id = ?", (pago_id,))
    if tipo_gasto == "Material / Producto":
        cursor.execute("""
            INSERT INTO especificaciones (proyecto_id, pago_id, rubro, ambiente, proveedor, producto_concepto, detalles_tecnicos) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (int(cursor.execute("SELECT proyecto_id FROM pagos WHERE id = ?", (pago_id,)).fetchone()[0]), pago_id, rubro, ambiente, proveedor, concepto, detalles_previos))
        
    conn.commit()
    conn.close()

def get_presupuestos(proyecto_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM presupuestos_rubro WHERE proyecto_id = ?", conn, params=(proyecto_id,))
    conn.close()
    return df

def guardar_presupuesto_rubro(proyecto_id, rubro, ambiente, proveedor, concepto, moneda, monto_presupuestado):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO rubros (nombre) VALUES (?)", (rubro,))
    cursor.execute("INSERT OR IGNORE INTO ambientes (nombre) VALUES (?)", (ambiente,))
    cursor.execute("""
        INSERT INTO presupuestos_rubro (proyecto_id, rubro, ambiente, proveedor, concepto, moneda, monto_presupuestado) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (proyecto_id, rubro, ambiente, proveedor, concepto, moneda, int(monto_presupuestado)))
    conn.commit()
    conn.close()

def actualizar_presupuesto(ppto_id, rubro, ambiente, proveedor, concepto, moneda, monto_presupuestado):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO rubros (nombre) VALUES (?)", (rubro,))
    cursor.execute("INSERT OR IGNORE INTO ambientes (nombre) VALUES (?)", (ambiente,))
    cursor.execute("""
        UPDATE presupuestos_rubro SET rubro = ?, ambiente = ?, proveedor = ?, concepto = ?, moneda = ?, monto_presupuestado = ? 
        WHERE id = ?
    """, (rubro, ambiente, proveedor, concepto, moneda, int(monto_presupuestado), ppto_id))
    conn.commit()
    conn.close()

def eliminar_presupuesto(ppto_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM presupuestos_rubro WHERE id = ?", (ppto_id,))
    conn.commit()
    conn.close()

def get_especificaciones(proyecto_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM especificaciones WHERE proyecto_id = ?", conn, params=(proyecto_id,))
    conn.close()
    return df

def actualizar_detalle_especificacion(esp_id, nuevos_detalles):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE especificaciones SET detalles_tecnicos = ? WHERE id = ?
    """, (nuevos_detalles, esp_id))
    conn.commit()
    conn.close()

# --- BARRA LATERAL: SELECCIÓN DE PROYECTO Y SESIÓN ---
st.sidebar.header("🏢 Selector de Proyecto")
df_proyectos = get_proyectos()

proyectos_dict = {f"ID {row['id']}: {row['nombre']} (Cliente: {row['cliente']})": row["id"] for idx, row in df_proyectos.iterrows()}
proyecto_sel_str = st.sidebar.selectbox("Seleccionar Proyecto Activo", list(proyectos_dict.keys()))
proyecto_id_activo = proyectos_dict[proyecto_sel_str]

proyecto_info = df_proyectos[df_proyectos["id"] == proyecto_id_activo].iloc[0]
sup_total = int(proyecto_info["superficie_total"])
precio_compra_proy = int(proyecto_info["precio_compra"])
presupuesto_ref = int(proyecto_info["presupuesto_reforma"])
precio_salida = int(proyecto_info["precio_objetivo"])

st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 **Sesión activa:** `{perfil}`")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.session_state.perfil = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("📊 Resumen del Proyecto")

df_pagos = get_pagos(proyecto_id_activo)
total_ejecutado = int(df_pagos["monto_usd"].sum()) if not df_pagos.empty else 0

gastos_compra_sidebar = int(precio_compra_proy * 0.08)
gastos_comercial = int(precio_salida * 0.06)
costo_total_est = (precio_compra_proy + gastos_compra_sidebar + presupuesto_ref)
profit_est = int(precio_salida - costo_total_est - gastos_comercial)
roi_est = int((profit_est / costo_total_est) * 100) if costo_total_est > 0 else 0

st.sidebar.metric("Superficie Total", f"{sup_total:,} m²".replace(",", "."))
st.sidebar.metric("CapEx Ejecutado Real", f"${total_ejecutado:,} USD".replace(",", "."))
st.sidebar.metric("Profit Estimado", f"${profit_est:,} USD".replace(",", "."))
st.sidebar.metric("ROI Neto Proyectado", f"{roi_est}%")

# --- INTERFAZ PRINCIPAL ---
st.title(f"🏗️ Panel Gerencial: {proyecto_info['nombre']}")
st.caption(f"Cliente / Inversor: {proyecto_info['cliente']} | Superficie: {sup_total} m²")

# Definición de Pestañas según el Perfil
if perfil == "Project Manager (Admin)":
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
        "💳 Registro de Pagos", "📐 Especificaciones", "📊 Módulo de Reportes", 
        "🏢 ABM Proyectos", "📑 ABM Proveedores", "🛠️ ABM Rubros", "🏠 ABM Ambientes",
        "💳 ABM Medios de Pago", "📋 ABM Presupuestos", "📈 Panel Financiero", "🚀 Escenarios Venta",
        "📥 Importar / Exportar"
    ])
else:
    tab_cli_1, tab_cli_2, tab_cli_3, tab_cli_4 = st.tabs([
        "📐 Bitácora Técnica", "📊 Reportes Ejecutivos", "📈 Panel Financiero", "🚀 Escenarios de Salida"
    ])

# ==========================================
# RENDERIZADORES DE MÓDULOS
# ==========================================

def render_especificaciones_tab():
    st.subheader("📐 Especificaciones y Bitácora Técnica (Catálogo de Materiales)")
    st.info(f"Catálogo de materiales y terminaciones aprobadas para {proyecto_info['nombre']}.")
    
    df_esp_actual = get_especificaciones(proyecto_id_activo)
    if not df_esp_actual.empty:
        st.markdown('<p class="field-title">Filtrar Bitácora por Ambiente:</p>', unsafe_allow_html=True)
        filtro_amb_esp = st.selectbox("Filtrar Bitácora por Ambiente:", ["Todos"] + list(df_esp_actual["ambiente"].dropna().unique()), label_visibility="collapsed")
        df_esp_viz = df_esp_actual.copy()
        if filtro_amb_esp != "Todos":
            df_esp_viz = df_esp_viz[df_esp_viz["ambiente"] == filtro_amb_esp]
            
        df_esp_display = df_esp_viz[["id", "rubro", "ambiente", "proveedor", "producto_concepto", "detalles_tecnicos"]].copy()
        df_esp_display.columns = ["N° Ítem", "Rubro", "Ambiente", "Proveedor", "Concepto", "Detalles Técnicos"]
        st.dataframe(df_esp_display, use_container_width=True)
        
        if perfil == "Project Manager (Admin)":
            st.markdown("### ✏️ Editar Detalle Técnico de un Producto")
            with st.form("form_editar_esp"):
                st.markdown('<p class="field-title">Seleccioná el N° de Ítem a editar</p>', unsafe_allow_html=True)
                ids_esp = df_esp_actual["id"].tolist()
                id_esp_sel = st.selectbox("Seleccioná el N° de Ítem a editar", ids_esp, label_visibility="collapsed")
                reg_esp_actual = df_esp_actual[df_esp_actual["id"] == id_esp_sel].iloc[0]
                
                st.markdown('<p class="field-title">Detalles Técnicos / Especificación Fina</p>', unsafe_allow_html=True)
                nuevo_detalle = st.text_area("Detalles Técnicos / Especificación Fina", value=str(reg_esp_actual["detalles_tecnicos"]), label_visibility="collapsed")
                
                if st.form_submit_button("💾 Actualizar Detalle Técnico"):
                    actualizar_detalle_especificacion(id_esp_sel, nuevo_detalle)
                    st.success("¡Detalle técnico actualizado correctamente!")
                    st.rerun()
    else:
        st.info("Aún no hay materiales o productos registrados en la bitácora.")

def render_reportes_tab():
    st.subheader("📊 Módulo de Reportes Gerenciales y Control Financiero Integral")
    st.markdown("Tablero centralizado con la comparativa Presupuesto vs. Real y estado de avance.")
    
    rep_tab1, rep_tab2 = st.tabs(["📈 Presupuesto vs. Real", "🚨 Control de Desviaciones"])
    
    with rep_tab1:
        st.markdown("### 📈 Reporte Detallado: Presupuesto vs. Real")
        df_ppto_rep = get_presupuestos(proyecto_id_activo)
        df_pagos_rep = get_pagos(proyecto_id_activo)
        
        tc_ref = 1250
        if not df_pagos_rep.empty and "tipo_cambio" in df_pagos_rep.columns:
            tc_prom = df_pagos_rep["tipo_cambio"].mean()
            if tc_prom > 0:
                tc_ref = int(tc_prom)
                
        if not df_ppto_rep.empty:
            if not df_pagos_rep.empty and "presupuesto_id" in df_pagos_rep.columns:
                df_ejec_agrupado = df_pagos_rep[df_pagos_rep["presupuesto_id"].notnull()].groupby("presupuesto_id")[["monto_ars", "monto_usd"]].sum().reset_index()
            else:
                df_ejec_agrupado = pd.DataFrame(columns=["presupuesto_id", "monto_ars", "monto_usd"])
                
            df_reporte = pd.merge(df_ppto_rep, df_ejec_agrupado, left_on="id", right_on="presupuesto_id", how="left").fillna(0)
            
            lista_filas = []
            for idx, row in df_reporte.iterrows():
                moneda_ppto = row["moneda"]
                monto_ppto = row["monto_presupuestado"]
                if moneda_ppto == "ARS":
                    ppto_ars = monto_ppto
                    ppto_usd = int(monto_ppto / tc_ref) if tc_ref > 0 else 0
                else:
                    ppto_usd = monto_ppto
                    ppto_ars = int(monto_ppto * tc_ref)
                    
                ejec_ars = int(row["monto_ars"])
                ejec_usd = int(row["monto_usd"])
                saldo_ars = ppto_ars - ejec_ars
                saldo_usd = ppto_usd - ejec_usd
                
                lista_filas.append({
                    "N° Ítem": row["id"],
                    "Rubro": row["rubro"],
                    "Ambiente": row["ambiente"],
                    "Proveedor": row["proveedor"],
                    "Concepto": row["concepto"],
                    "Ppto (ARS)": ppto_ars,
                    "Ppto (USD)": ppto_usd,
                    "Ejec (ARS)": ejec_ars,
                    "Ejec (USD)": ejec_usd,
                    "Saldo (ARS)": saldo_ars,
                    "Saldo (USD)": saldo_usd
                })
                
            df_final_rep = pd.DataFrame(lista_filas)
            
            total_p_ars = int(df_ppto_rep.apply(lambda r: r["monto_presupuestado"] if r["moneda"] == "ARS" else r["monto_presupuestado"] * tc_ref, axis=1).sum())
            total_p_usd = int(df_ppto_rep.apply(lambda r: r["monto_presupuestado"] if r["moneda"] == "USD" else int(r["monto_presupuestado"] / tc_ref), axis=1).sum())
            total_e_ars = int(df_pagos_rep["monto_ars"].sum()) if not df_pagos_rep.empty else 0
            total_e_usd = int(df_pagos_rep["monto_usd"].sum()) if not df_pagos_rep.empty else 0
            
            col_tot1, col_tot2 = st.columns(2)
            with col_tot1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Ejecutado vs. Presupuestado (ARS)</div>
                        <div class="metric-value">${total_e_ars:,} / ${total_p_ars:,} ARS</div>
                    </div>
                """.replace(",", "."), unsafe_allow_html=True)
            with col_tot2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Ejecutado vs. Presupuestado (USD)</div>
                        <div class="metric-value">${total_e_usd:,} / ${total_p_usd:,} USD</div>
                    </div>
                """.replace(",", "."), unsafe_allow_html=True)
                
            st.markdown("---")
            df_viz = df_final_rep.copy()
            for col in ["Ppto (ARS)", "Ppto (USD)", "Ejec (ARS)", "Ejec (USD)", "Saldo (ARS)", "Saldo (USD)"]:
                df_viz[col] = df_viz[col].apply(lambda x: f"${int(x):,}".replace(",", "."))
            st.dataframe(df_viz, use_container_width=True)
        else:
            st.info("No hay presupuestos cargados para este proyecto.")

    with rep_tab2:
        st.markdown("### 🚨 Control de Desviaciones por Partida")
        df_ppto_check = get_presupuestos(proyecto_id_activo)
        df_pagos_rep = get_pagos(proyecto_id_activo)
        
        if not df_ppto_check.empty:
            tc_ref = 1250
            if not df_pagos_rep.empty and "tipo_cambio" in df_pagos_rep.columns:
                tc_prom = df_pagos_rep["tipo_cambio"].mean()
                if tc_prom > 0:
                    tc_ref = int(tc_prom)
                    
            df_ejec_check = df_pagos_rep[df_pagos_rep["presupuesto_id"].notnull()].groupby("presupuesto_id")[["monto_ars", "monto_usd"]].sum().reset_index()
            df_desv = pd.merge(df_ppto_check, df_ejec_check, left_on="id", right_on="presupuesto_id", how="left").fillna(0)
            
            lista_desv = []
            for idx, row in df_desv.iterrows():
                moneda = row["moneda"]
                monto_ppto = row["monto_presupuestado"]
                if moneda == "ARS":
                    ppto_ars = monto_ppto
                else:
                    ppto_ars = int(monto_ppto * tc_ref)
                    
                ejec_ars = int(row["monto_ars"])
                pct_ejecutado = int((ejec_ars / ppto_ars) * 100) if ppto_ars > 0 else 0
                
                if pct_ejecutado > 100:
                    alerta = "🔴 EXCEDIDO"
                elif pct_ejecutado >= 85:
                    alerta = "🟡 AL LÍMITE"
                else:
                    alerta = "🟢 EN ORDEN"
                    
                lista_desv.append({
                    "N° Ítem": row["id"],
                    "Rubro": row["rubro"],
                    "Ambiente": row["ambiente"],
                    "Concepto": row["concepto"],
                    "Presupuestado": f"${monto_ppto:,} {moneda}".replace(",", "."),
                    "Ejecutado": f"${ejec_ars:,} ARS".replace(",", "."),
                    "% Ejec.": f"{pct_ejecutado}%",
                    "Estado": alerta
                })
            st.dataframe(pd.DataFrame(lista_desv), use_container_width=True)
        else:
            st.info("Cargá partidas presupuestarias para activar el control.")

def render_panel_financiero():
    st.subheader("📊 Análisis y Distribución del CapEx")
    st.markdown("Distribución gráfica de erogaciones reales por **Rubro de Obra** y **Ambiente**.")
    
    df_pagos_fin = get_pagos(proyecto_id_activo)
    if not df_pagos_fin.empty:
        fin_tab_rubro, fin_tab_ambiente = st.tabs([
            "📂 Distribución por Rubro", "🏠 Distribución por Ambiente"
        ])
        
        colores_pasteles = ["#94B3FD", "#B9E4C9", "#FCE38A", "#F38181", "#E2D7F7", "#FFD166", "#A0C4FF", "#CAFFBF"]
        
        with fin_tab_rubro:
            st.markdown("### 📂 Análisis de Gastos por Rubro de Obra")
            df_rubro_agg = df_pagos_fin.groupby("rubro")[["monto_usd", "monto_ars"]].sum().reset_index()
            total_usd_gen = df_rubro_agg["monto_usd"].sum()
            df_rubro_agg["porcentaje"] = ((df_rubro_agg["monto_usd"] / total_usd_gen) * 100).round(1)
            
            col_r1, col_r2 = st.columns([1.3, 0.9])
            with col_r1:
                fig_rubro = px.pie(df_rubro_agg, values="monto_usd", names="rubro", title=f"Participación por Rubro (USD)", hole=0.4, color_discrete_sequence=colores_pasteles)
                fig_rubro.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="sans-serif", color="#2d3748"))
                st.plotly_chart(fig_rubro, use_container_width=True)
            with col_r2:
                st.markdown('<div style="margin-top: 45px;"><p style="color:#3182ce; font-weight:400; font-size:13px; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:12px;">📌 Referencia y %</p></div>', unsafe_allow_html=True)
                for idx, row in df_rubro_agg.iterrows():
                    st.markdown(f"<span style='font-size:13px; color:#4a5568;'><b>{row['rubro']}</b>:<br>🔹 <b>{row['porcentaje']}%</b> (${int(row['monto_usd']):,} USD)</span><br><br>", unsafe_allow_html=True)
                    
            st.markdown("---")
            df_rubro_table = df_rubro_agg[["rubro", "monto_usd", "monto_ars", "porcentaje"]].copy()
            df_rubro_table["monto_usd"] = df_rubro_table["monto_usd"].apply(lambda x: f"${int(x):,} USD".replace(",", "."))
            df_rubro_table["monto_ars"] = df_rubro_table["monto_ars"].apply(lambda x: f"${int(x):,} ARS".replace(",", "."))
            df_rubro_table["porcentaje"] = df_rubro_table["porcentaje"].apply(lambda x: f"{x}%")
            df_rubro_table.columns = ["Rubro de Obra", "Total (USD)", "Total (ARS)", "% del Total"]
            st.dataframe(df_rubro_table, use_container_width=True)
            
        with fin_tab_ambiente:
            st.markdown("### 🏠 Análisis de Gastos por Ambiente")
            df_amb_agg = df_pagos_fin.groupby("ambiente")[["monto_usd", "monto_ars"]].sum().reset_index()
            total_usd_amb = df_amb_agg["monto_usd"].sum()
            df_amb_agg["porcentaje"] = ((df_amb_agg["monto_usd"] / total_usd_amb) * 100).round(1)
            
            col_a1, col_a2 = st.columns([1.3, 0.9])
            with col_a1:
                fig_amb = px.pie(df_amb_agg, values="monto_usd", names="ambiente", title=f"Participación por Ambiente (USD)", hole=0.4, color_discrete_sequence=colores_pasteles)
                fig_amb.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="sans-serif", color="#2d3748"))
                st.plotly_chart(fig_amb, use_container_width=True)
            with col_a2:
                st.markdown('<div style="margin-top: 45px;"><p style="color:#3182ce; font-weight:400; font-size:13px; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:12px;">📌 Referencia y %</p></div>', unsafe_allow_html=True)
                for idx, row in df_amb_agg.iterrows():
                    st.markdown(f"<span style='font-size:13px; color:#4a5568;'><b>{row['ambiente']}</b>:<br>🔹 <b>{row['porcentaje']}%</b> (${int(row['monto_usd']):,} USD)</span><br><br>", unsafe_allow_html=True)
                    
            st.markdown("---")
            df_amb_table = df_amb_agg[["ambiente", "monto_usd", "monto_ars", "porcentaje"]].copy()
            df_amb_table["monto_usd"] = df_amb_table["monto_usd"].apply(lambda x: f"${int(x):,} USD".replace(",", "."))
            df_amb_table["monto_ars"] = df_amb_table["monto_ars"].apply(lambda x: f"${int(x):,} ARS".replace(",", "."))
            df_amb_table["porcentaje"] = df_amb_table["porcentaje"].apply(lambda x: f"{x}%")
            df_amb_table.columns = ["Ambiente", "Total (USD)", "Total (ARS)", "% del Total"]
            st.dataframe(df_amb_table, use_container_width=True)
    else:
        st.info("Carga pagos para visualizar los gráficos y porcentajes.")

def render_escenarios_venta():
    st.subheader("🚀 Modelado de Escenarios de Venta y Viabilidad Financiera")
    st.markdown("Simulador profesional de salida y rentabilidad del proyecto.")
    
    sup_m2 = float(sup_total)
    precio_compra_base = int(precio_compra_proy)
    gastos_compra = int(precio_compra_base * 0.08)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown(f"**Superficie:** {sup_m2} m² | **Compra:** ${precio_compra_base:,} USD".replace(",", "."))
    with col_p2:
        remodelacion_input = st.number_input("Remodelación Escenario (USD)", min_value=0, value=int(presupuesto_ref), step=5000, format="%d")
    with col_p3:
        modo_ingreso_val = st.radio("Método de Cotización", ["Valor Total (USD)", "Valor por m² (USD/m²)"], horizontal=True)
        
    if modo_ingreso_val == "Valor Total (USD)":
        val_mercado_total = st.number_input("Valor de Mercado Total (USD)", min_value=50000, value=520000, step=10000, format="%d")
        st.caption(f"💡 Ingresado como Valor Global Total: **${val_mercado_total:,} USD**".replace(",", "."))
    else:
        val_m2_mercado = st.number_input("Valor de Mercado (USD/m²)", min_value=500, value=3800, step=100, format="%d")
        val_mercado_total = int(val_m2_mercado * sup_m2)
        st.caption(f"💡 Calculado (${val_m2_mercado:,} USD/m² × {sup_m2} m²): **${val_mercado_total:,} USD**".replace(",", "."))
    
    pes_vta = int(val_mercado_total * 0.95)
    con_vta = val_mercado_total
    opt_vta = int(val_mercado_total * 1.12)
    
    costo_inversion_total = (precio_compra_base + gastos_compra + remodelacion_input + 5000)
    
    def calcular_resultado_escenario(precio_vta):
        gastos_vta = int(precio_vta * 0.06)
        profit = precio_vta - (costo_inversion_total + gastos_vta)
        roi = int((profit / costo_inversion_total) * 100) if costo_inversion_total > 0 else 0
        dif_mercado_pct = ((precio_vta - val_mercado_total) / val_mercado_total) * 100 if val_mercado_total > 0 else 0
        return gastos_vta, profit, roi, dif_mercado_pct
        
    pes_gventa, pes_profit, pes_roi, pes_dif = calcular_resultado_escenario(pes_vta)
    con_gventa, con_profit, con_roi, con_dif = calcular_resultado_escenario(con_vta)
    opt_gventa, opt_profit, opt_roi, opt_dif = calcular_resultado_escenario(opt_vta)
    
    res1, res2, res3 = st.columns(3)
    
    def mostrar_tabla_escenario(titulo, gventa, profit, roi, dif, v_venta):
        st.markdown(f"#### {titulo}")
        df_tabla_esc = pd.DataFrame({
            "Indicador Financiero": ["Valor de Venta", "Costo Total Inversión", "Ganancia Total (USD)", "ROI Neto", "Dif. Mercado"],
            "Valor del Escenario": [
                f"${v_venta:,} USD".replace(",", "."), f"${costo_inversion_total:,} USD".replace(",", "."), 
                f"${profit:,} USD".replace(",", "."), f"{roi}%", f"{round(dif, 1)}%"
            ]
        })
        st.dataframe(df_tabla_esc, use_container_width=True, hide_index=True)
        
        if roi < 0:
            st.error("🚨 ¡Pérdida financiera! Inversión no viable en este escenario.")
        elif roi < 10:
            st.warning("⚠️ Margen ajustado o moderado. Analizar riesgos.")
        else:
            st.success("✅ Excelente rentabilidad proyectada.")
            
    with res1:
        mostrar_tabla_escenario("📉 Pesimista", pes_gventa, pes_profit, pes_roi, pes_dif, pes_vta)
    with res2:
        mostrar_tabla_escenario("📊 Conservador", con_gventa, con_profit, con_roi, con_dif, con_vta)
    with res3:
        mostrar_tabla_escenario("🚀 Optimista", opt_gventa, opt_profit, opt_roi, opt_dif, opt_vta)

# --- ENRUTAMIENTO SEGÚN PERFIL ---
if perfil == "Project Manager (Admin)":
    with tab1:
        st.subheader("➕ Cargar Nuevo Gasto / Pago")
        df_ppto_disponibles = get_presupuestos(proyecto_id_activo)
        ppto_opciones = {"Sin asociar (Gasto libre)": None}
        if not df_ppto_disponibles.empty:
            for idx, row in df_ppto_disponibles.iterrows():
                label_ppto = f"N° Ítem {row['id']} | Rubro: {row['rubro']} | Amb: {row['ambiente']} | Prov: {row['proveedor']} | Tarea: {row['concepto']} ({row['monto_presupuestado']:,} {row['moneda']})"
                ppto_opciones[label_ppto] = row["id"]
                
        with st.form("form_pago", clear_on_submit=True):
            st.markdown('<p class="field-title">Vincular con Partida Presupuestaria (Opcional)</p>', unsafe_allow_html=True)
            c_asoc = st.selectbox("Vincular con Partida Presupuestaria (Opcional)", list(ppto_opciones.keys()), label_visibility="collapsed")
            presupuesto_id_sel = ppto_opciones[c_asoc]
            
            col_0, col_a, col_mp, col_cuotas = st.columns(4)
            with col_0:
                st.markdown('<p class="field-title">🏷️ Tipo de Gasto</p>', unsafe_allow_html=True)
                tipo_gasto_sel = st.selectbox("Tipo Gasto", ["Material / Producto", "Servicio"], label_visibility="collapsed")
            with col_a:
                st.markdown('<p class="field-title">🧾 N° Comprobante</p>', unsafe_allow_html=True)
                comprobante_sel = st.text_input("Comprobante", value="", placeholder="Ej: FC 0001-12345", label_visibility="collapsed")
            with col_mp:
                st.markdown('<p class="field-title">💳 Medio de Pago</p>', unsafe_allow_html=True)
                medio_pago_sel = st.selectbox("Medio Pago", get_medios_pago(), label_visibility="collapsed")
            with col_cuotas:
                st.markdown('<p class="field-title">🔢 Cantidad de Cuotas</p>', unsafe_allow_html=True)
                cuotas_sel = st.number_input("Cuotas", min_value=1, value=1, step=1, format="%d", label_visibility="collapsed")
                
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown('<p class="field-title">📅 Fecha de Pago</p>', unsafe_allow_html=True)
                fecha_pago = st.date_input("Fecha", value=datetime.today(), label_visibility="collapsed")
            with col2:
                st.markdown('<p class="field-title">📂 Rubro de Obra</p>', unsafe_allow_html=True)
                rubro_sel = st.selectbox("Rubro", get_rubros(), label_visibility="collapsed")
            with col3:
                st.markdown('<p class="field-title">🏠 Ambiente</p>', unsafe_allow_html=True)
                ambiente_sel = st.selectbox("Ambiente", get_ambientes(), label_visibility="collapsed")
            with col4:
                st.markdown('<p class="field-title">📑 Proveedor</p>', unsafe_allow_html=True)
                proveedor_sel = st.selectbox("Proveedor", get_proveedores(), label_visibility="collapsed")
                
            col5, col6, col7 = st.columns(3)
            with col5:
                st.markdown('<p class="field-title">💬 Concepto</p>', unsafe_allow_html=True)
                concepto = st.text_input("Concepto", value="", placeholder="Ej: Porcelanato", label_visibility="collapsed")
            with col6:
                st.markdown('<p class="field-title">💵 Monto en ARS ($)</p>', unsafe_allow_html=True)
                monto_ars = st.number_input("Monto ARS", min_value=0, value=0, step=10000, format="%d", label_visibility="collapsed")
            with col7:
                st.markdown('<p class="field-title">💱 Tipo de Cambio (USD)</p>', unsafe_allow_html=True)
                tipo_cambio = st.number_input("Tipo de Cambio", min_value=1, value=1250, step=10, format="%d", label_visibility="collapsed")
                
            if st.form_submit_button("💾 Guardar Pago en SQLite") and proveedor_sel and concepto:
                agregar_pago(proyecto_id_activo, presupuesto_id_sel, str(fecha_pago), comprobante_sel, tipo_gasto_sel, medio_pago_sel, cuotas_sel, rubro_sel, ambiente_sel, proveedor_sel, concepto, monto_ars, tipo_cambio)
                st.success("¡Gasto guardado correctamente!")
                st.rerun()
                
        st.markdown("---")
        st.subheader("📋 Historial Completo de Erogaciones y Gestión")
        df_pagos_actual = get_pagos(proyecto_id_activo)
        
        if not df_pagos_actual.empty:
            df_display = df_pagos_actual[["id", "fecha", "comprobante", "tipo_gasto", "medio_pago", "cuotas", "rubro", "ambiente", "proveedor", "concepto", "monto_ars", "tipo_cambio", "monto_usd"]].copy()
            df_display["monto_ars"] = df_display["monto_ars"].apply(lambda x: f"${int(x):,}".replace(",", "."))
            df_display["monto_usd"] = df_display["monto_usd"].apply(lambda x: f"${int(x):,}".replace(",", "."))
            df_display.columns = ["N°", "Fecha", "Comp.", "Tipo", "Medio Pago", "Cuotas", "Rubro", "Ambiente", "Proveedor", "Concepto", "Monto (ARS)", "TC", "Monto (USD)"]
            st.dataframe(df_display, use_container_width=True)
            
            st.markdown("### ✏️ Modificar o Eliminar un Registro de Pago")
            ids_disponibles = df_pagos_actual["id"].tolist()
            id_a_gestionar = st.selectbox("Seleccioná el N° de pago a editar o borrar", ids_disponibles, label_visibility="collapsed")
            reg_sel = df_pagos_actual[df_pagos_actual["id"] == id_a_gestionar].iloc[0]
            
            with st.form("form_editar_pago"):
                st.markdown(f"**Editando Registro N°: {id_a_gestionar}**")
                e_monto = st.number_input("Monto ARS", value=int(reg_sel["monto_ars"]), step=10000, format="%d")
                e_tc = st.number_input("Tipo de Cambio", value=int(reg_sel["tipo_cambio"]) if reg_sel["tipo_cambio"] > 0 else 1250, step=10, format="%d")
                
                btn_modificar = st.form_submit_button("🔄 Actualizar Pago")
                btn_eliminar = st.form_submit_button("🗑️ Eliminar este Pago")
                
                if btn_modificar:
                    actualizar_pago_completo(id_a_gestionar, reg_sel["presupuesto_id"], reg_sel["fecha"], reg_sel["comprobante"], reg_sel["tipo_gasto"], reg_sel["medio_pago"], reg_sel["cuotas"], reg_sel["rubro"], reg_sel["ambiente"], reg_sel["proveedor"], reg_sel["concepto"], e_monto, e_tc)
                    st.success("¡Actualizado con éxito!")
                    st.rerun()
                if btn_eliminar:
                    eliminar_pago(id_a_gestionar)
                    st.success("¡Eliminado correctamente!")
                    st.rerun()
        else:
            st.info("No hay pagos cargados para este proyecto todavía.")

    with tab2:
        render_especificaciones_tab()
    with tab3:
        render_reportes_tab()
    with tab4:
        st.subheader("🏢 ABM de Proyectos y Clientes")
        with st.form("form_nuevo_proyecto", clear_on_submit=True):
            np_nombre = st.text_input("Nombre del Proyecto", label_visibility="collapsed")
            np_cliente = st.text_input("Nombre del Cliente", label_visibility="collapsed")
            np_sup = st.number_input("Superficie Total (m²)", min_value=10, value=100, step=1, format="%d", label_visibility="collapsed")
            np_compra = st.number_input("Precio Compra (USD)", min_value=10000, value=250000, step=10000, format="%d", label_visibility="collapsed")
            np_ref = st.number_input("Presupuesto Reforma (USD)", min_value=1000, value=50000, step=5000, format="%d", label_visibility="collapsed")
            np_salida = st.number_input("Precio Venta Objetivo (USD)", min_value=10000, value=350000, step=10000, format="%d", label_visibility="collapsed")
            
            if st.form_submit_button("➕ Crear Proyecto") and np_nombre:
                conn_tmp = sqlite3.connect(DB_NAME)
                cursor_tmp = conn_tmp.cursor()
                cursor_tmp.execute("INSERT INTO proyectos (nombre, cliente, superficie_total, precio_compra, presupuesto_reforma, precio_objetivo) VALUES (?, ?, ?, ?, ?, ?)", 
                                   (np_nombre, np_cliente, np_sup, np_compra, np_ref, np_salida))
                conn_tmp.commit()
                conn_tmp.close()
                st.success("¡Proyecto creado!")
                st.rerun()
        st.dataframe(get_proyectos(), use_container_width=True)

    with tab5:
        st.subheader("📑 ABM de Proveedores")
        with st.form("form_nuevo_proveedor", clear_on_submit=True):
            p_nombre = st.text_input("Nombre Proveedor", label_visibility="collapsed")
            p_rubro = st.selectbox("Rubro Principal", get_rubros(), label_visibility="collapsed")
            p_contacto = st.text_input("Contacto", label_visibility="collapsed")
            if st.form_submit_button("➕ Guardar") and p_nombre:
                conn_tmp = sqlite3.connect(DB_NAME)
                cursor_tmp = conn_tmp.cursor()
                cursor_tmp.execute("INSERT INTO proveedores (nombre, rubro_principal, contacto) VALUES (?, ?, ?)", (p_nombre, p_rubro, p_contacto))
                conn_tmp.commit()
                conn_tmp.close()
                st.success("¡Guardado!")
                st.rerun()
        st.dataframe(get_proveedores_df(), use_container_width=True)

    with tab6:
        st.subheader("🛠️ ABM de Rubros (Sincronizado con Pagos)")
        with st.form("form_nuevo_rubro", clear_on_submit=True):
            nuevo_cat = st.text_input("Nombre del Rubro", label_visibility="collapsed")
            if st.form_submit_button("➕ Agregar") and nuevo_cat:
                conn_tmp = sqlite3.connect(DB_NAME)
                cursor_tmp = conn_tmp.cursor()
                cursor_tmp.execute("INSERT OR IGNORE INTO rubros (nombre) VALUES (?)", (nuevo_cat,))
                conn_tmp.commit()
                conn_tmp.close()
                st.success("¡Agregado!")
                st.rerun()
        st.dataframe(get_rubros_df(), use_container_width=True)

    with tab7:
        st.subheader("🏠 ABM de Ambientes (Sincronizado con Pagos)")
        with st.form("form_nuevo_ambiente", clear_on_submit=True):
            nuevo_amb = st.text_input("Nombre del Ambiente", label_visibility="collapsed")
            if st.form_submit_button("➕ Agregar Ambiente") and nuevo_amb:
                conn_tmp = sqlite3.connect(DB_NAME)
                cursor_tmp = conn_tmp.cursor()
                cursor_tmp.execute("INSERT OR IGNORE INTO ambientes (nombre) VALUES (?)", (nuevo_amb,))
                conn_tmp.commit()
                conn_tmp.close()
                st.success("¡Ambiente agregado!")
                st.rerun()
        st.dataframe(get_ambientes_df(), use_container_width=True)

    with tab8:
        st.subheader("💳 ABM de Medios de Pago")
        with st.form("form_nuevo_mp", clear_on_submit=True):
            mp_nombre = st.text_input("Nombre Medio", label_visibility="collapsed")
            mp_tipo = st.selectbox("Tipo", ["Tarjeta de Crédito", "Transferencia", "Efectivo", "Cheque", "Otro"], label_visibility="collapsed")
            mp_detalle = st.text_input("Detalle", label_visibility="collapsed")
            if st.form_submit_button("➕ Guardar") and mp_nombre:
                conn_tmp = sqlite3.connect(DB_NAME)
                cursor_tmp = conn_tmp.cursor()
                cursor_tmp.execute("INSERT INTO medios_pago (nombre, tipo, detalle) VALUES (?, ?, ?)", (mp_nombre, mp_tipo, mp_detalle))
                conn_tmp.commit()
                conn_tmp.close()
                st.success("¡Guardado!")
                st.rerun()
        st.dataframe(get_medios_pago_df(), use_container_width=True)

    with tab9:
        st.subheader("📋 ABM de Presupuestos")
        with st.form("form_pto_rubro", clear_on_submit=True):
            p_rubro = st.selectbox("Rubro Ppto", get_rubros(), label_visibility="collapsed")
            p_prov = st.selectbox("Proveedor Ppto", get_proveedores(), label_visibility="collapsed")
            p_ambiente = st.selectbox("Ambiente Ppto", get_ambientes(), label_visibility="collapsed")
            p_concepto = st.text_input("Concepto", value="Provisión y colocación", label_visibility="collapsed")
            p_moneda = st.selectbox("Moneda", ["ARS", "USD"], label_visibility="collapsed")
            p_monto = st.number_input("Monto", min_value=0, value=500000, step=10000, format="%d", label_visibility="collapsed")
            if st.form_submit_button("💾 Guardar Presupuesto") and p_concepto:
                guardar_presupuesto_rubro(proyecto_id_activo, p_rubro, p_ambiente, p_prov, p_concepto, p_moneda, p_monto)
                st.success("¡Guardado!")
                st.rerun()
        st.dataframe(get_presupuestos(proyecto_id_activo), use_container_width=True)

    with tab10:
        render_panel_financiero()
    with tab11:
        render_escenarios_venta()
    with tab12:
        st.subheader("📥 Importar y Exportar Planillas (Presupuestos y Pagos)")
        st.markdown("Descargá las plantillas vacías, completalas en Excel y subilas para cargar masivamente los datos en el proyecto activo.")
        
        # Botón de emergencia para vaciar pagos y reiniciar carga
        st.markdown("---")
        st.warning("⚠️ **Zona de Mantenimiento:** Si querés limpiar todos los pagos duplicados y empezar de cero con la importación, hacé clic acá:")
        if st.button("🗑️ VACIAR TODA LA TABLA DE PAGOS"):
            eliminar_todos_los_pagos(proyecto_id_activo)
            st.success("¡Todos los pagos fueron eliminados con éxito! Ya podés reimportar tu planilla limpia.")
            st.rerun()
        st.markdown("---")

        imp_sub1, imp_sub2 = st.tabs(["📥 Descargar Plantillas", "📤 Subir / Importar Planillas"])
        
        with imp_sub1:
            st.markdown("### 📥 Plantillas de Ejemplo para Descargar")
            
            df_plantilla_ppto = pd.DataFrame([{
                "rubro": "Demolición y Albañilería",
                "ambiente": "Cocina",
                "proveedor": "SBG",
                "concepto": "Picado de revoques y mampostería",
                "moneda": "USD",
                "monto_presupuestado": 3500
            }])
            csv_ppto = df_plantilla_ppto.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Plantilla CSV de Presupuestos", data=csv_ppto, file_name="plantilla_presupuestos.csv", mime="text/csv")
            
            st.markdown("---")
            
            df_plantilla_pagos = pd.DataFrame([{
                "presupuesto_id": 1,
                "fecha": "2026-06-01",
                "comprobante": "FC 0001-00012345",
                "tipo_gasto": "Material / Producto",
                "medio_pago": "Visa Galicia (Principal)",
                "cuotas": 3,
                "rubro": "Demolición y Albañilería",
                "ambiente": "Cocina",
                "proveedor": "SBG",
                "concepto": "Acopio de materiales",
                "monto_ars": 1250000,
                "tipo_cambio": 1250
            }])
            csv_pagos = df_plantilla_pagos.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Plantilla CSV de Pagos", data=csv_pagos, file_name="plantilla_pagos.csv", mime="text/csv")
            
        with imp_sub2:
            st.markdown("### 📤 Carga Masiva desde CSV")
            
            tipo_carga = st.selectbox("Seleccioná qué querés importar", ["Presupuestos", "Pagos"])
            archivo_subido = st.file_uploader(f"Subir archivo CSV de {tipo_carga}", type=["csv"])
            
            if archivo_subido is not None:
                try:
                    df_upload = pd.read_csv(archivo_subido)
                    st.markdown("#### Vista previa de los datos a importar:")
                    st.dataframe(df_upload, use_container_width=True)
                    
                    if st.button(f"🚀 Importar {tipo_carga} al Proyecto Activo"):
                        conn_imp = sqlite3.connect(DB_NAME)
                        cursor_imp = conn_imp.cursor()
                        
                        if tipo_carga == "Presupuestos":
                            for idx, row in df_upload.iterrows():
                                r_val = str(row["rubro"])
                                a_val = str(row["ambiente"])
                                cursor_imp.execute("INSERT OR IGNORE INTO rubros (nombre) VALUES (?)", (r_val,))
                                cursor_imp.execute("INSERT OR IGNORE INTO ambientes (nombre) VALUES (?)", (a_val,))
                                
                                cursor_imp.execute("""
                                    INSERT INTO presupuestos_rubro (proyecto_id, rubro, ambiente, proveedor, concepto, moneda, monto_presupuestado)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (proyecto_id_activo, r_val, a_val, row["proveedor"], row["concepto"], row["moneda"], int(row["monto_presupuestado"])))
                            conn_imp.commit()
                            st.success(f"¡Se importaron {len(df_upload)} presupuestos con éxito y se actualizaron los ABM!")
                            
                        elif tipo_carga == "Pagos":
                            for idx, row in df_upload.iterrows():
                                p_id = int(row["presupuesto_id"]) if pd.notnull(row["presupuesto_id"]) and str(row["presupuesto_id"]).strip() != "" else None
                                
                                m_ars_val = str(row["monto_ars"]).replace(",", "").replace(".", "").replace("$", "").strip()
                                m_ars = int(float(m_ars_val)) if m_ars_val else 0
                                
                                tc_val = str(row["tipo_cambio"]).replace(",", "").replace(".", "").replace("$", "").strip()
                                tc = int(float(tc_val)) if tc_val and float(tc_val) > 0 else 1250
                                
                                m_usd = int(m_ars / tc) if tc > 0 else 0
                                r_val = str(row["rubro"])
                                a_val = str(row["ambiente"])
                                
                                cursor_imp.execute("INSERT OR IGNORE INTO rubros (nombre) VALUES (?)", (r_val,))
                                cursor_imp.execute("INSERT OR IGNORE INTO ambientes (nombre) VALUES (?)", (a_val,))
                                
                                cursor_imp.execute("""
                                    INSERT INTO pagos (proyecto_id, presupuesto_id, fecha, comprobante, tipo_gasto, medio_pago, cuotas, rubro, ambiente, proveedor, concepto, monto_ars, tipo_cambio, monto_usd)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    proyecto_id_activo, 
                                    p_id, 
                                    str(row["fecha"]), 
                                    str(row["comprobante"]), 
                                    str(row["tipo_gasto"]), 
                                    str(row["medio_pago"]), 
                                    int(row["cuotas"]), 
                                    r_val, 
                                    a_val, 
                                    str(row["proveedor"]), 
                                    str(row["concepto"]), 
                                    m_ars, 
                                    tc, 
                                    m_usd
                                ))
                                
                                new_pago_id = cursor_imp.lastrowid
                                if str(row["tipo_gasto"]) == "Material / Producto":
                                    cursor_imp.execute("""
                                        INSERT INTO especificaciones (proyecto_id, pago_id, rubro, ambiente, proveedor, producto_concepto, detalles_tecnicos)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        proyecto_id_activo, 
                                        new_pago_id, 
                                        r_val, 
                                        a_val, 
                                        str(row["proveedor"]), 
                                        str(row["concepto"]), 
                                        "Pendiente de detalle técnico..."
                                    ))
                                    
                            conn_imp.commit()
                            st.success(f"¡Se importaron {len(df_upload)} pagos con éxito y se actualizaron los ABM de Rubros y Ambientes!")
                            
                        conn_imp.close()
                        st.rerun()
                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el archivo: {e}")

else:
    # VISTA CLIENTE
    with tab_cli_1:
        render_especificaciones_tab()
    with tab_cli_2:
        render_reportes_tab()
    with tab_cli_3:
        render_panel_financiero()
    with tab_cli_4:
        render_escenarios_venta()
