from datetime import datetime
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS UNIFICADOS (ESTILO REVALORIZA) ---
st.set_page_config(
    page_title="Gestión Flipping Multi-Proyecto",
    layout="wide"
)

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

/* UNIFICACIÓN VISUAL: Títulos/Etiquetas de campos en formularios y filtros (Mayúsculas, sin negrita, azul suave) */  
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

/* UNIFICACIÓN GLOBAL DE TABLAS: Cabeceras en azul suave, mayúsculas, sin negrita, sin saltos de línea */  
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
    padding-top: 8px !important;  
    padding-bottom: 8px !important;  
    color: #2d3748 !important;  
}  
</style>  
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE LA BASE DE DATOS SQLITE ---
DB_NAME = "flipping_multiproyecto.db"

# --- CONEXIÓN A SUPABASE CON STREAMLIT ---
import streamlit as st
import requests

# --- CONEXIÓN DIRECTA Y SEGURA A SUPABASE ---
def init_db():
    # Creamos un objeto de conexión compatible con tus consultas
    return st.secrets["postgres"]["url"]
    
    # 1. Tabla de Proyectos
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
    
    # 2. Tabla de Proveedores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            rubro_principal TEXT,
            contacto TEXT
        )
    """)
    
    # 3. Tabla de Rubros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rubros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)
    
    # 4. Tabla de Medios de Pago (ABM)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medios_pago (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            tipo TEXT,
            detalle TEXT
        )
    """)
    
    # 5. Tabla de Presupuestos por Rubro
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
    
    # 6. Tabla de Pagos
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
    
    # 7. Tabla de Especificaciones / Bitácora Técnica
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
    
    # Insertar proyecto inicial por defecto (Coronel Díaz)
    cursor.execute("SELECT COUNT(*) FROM proyectos")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO proyectos (id, nombre, cliente, superficie_total, precio_compra, presupuesto_reforma, precio_objetivo) 
            VALUES (1, 'Coronel Díaz 2109 5° A', 'Verona', 137, 350000, 90000, 580000)
        """)
        conn.commit()
        
    # Rubros iniciales
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
        
    # Proveedores iniciales
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
        
    # Medios de pago iniciales
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

# --- FUNCIONES DE BASE DE DATOS ---
def get_proyectos():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM proyectos", conn)
    conn.close()
    return df

def agregar_proyecto(nombre, cliente, superficie_total, precio_compra, presupuesto_reforma, precio_objetivo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO proyectos (nombre, cliente, superficie_total, precio_compra, presupuesto_reforma, precio_objetivo) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, cliente, superficie_total, precio_compra, presupuesto_reforma, precio_objetivo))
        conn.commit()
        exito = True
    except sqlite3.IntegrityError:
        exito = False
    conn.close()
    return exito

def actualizar_proyecto(p_id, nombre, cliente, superficie_total, precio_compra, presupuesto_reforma, precio_objetivo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE proyectos SET nombre = ?, cliente = ?, superficie_total = ?, precio_compra = ?, presupuesto_reforma = ?, precio_objetivo = ? 
        WHERE id = ?
    """, (nombre, cliente, superficie_total, precio_compra, presupuesto_reforma, precio_objetivo, p_id))
    conn.commit()
    conn.close()

def eliminar_proyecto(p_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proyectos WHERE id = ?", (p_id,))
    conn.commit()
    conn.close()

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

def agregar_proveedor(nombre, rubro, contacto):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO proveedores (nombre, rubro_principal, contacto) VALUES (?, ?, ?)", (nombre, rubro, contacto))
        conn.commit()
        exito = True
    except sqlite3.IntegrityError:
        exito = False
    conn.close()
    return exito

def actualizar_proveedor(prov_id, nombre, rubro, contacto):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE proveedores SET nombre = ?, rubro_principal = ?, contacto = ? WHERE id = ?
    """, (nombre, rubro, contacto, prov_id))
    conn.commit()
    conn.close()

def eliminar_proveedor(prov_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proveedores WHERE id = ?", (prov_id,))
    conn.commit()
    conn.close()

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

def agregar_rubro(nuevo_rubro):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO rubros (nombre) VALUES (?)", (nuevo_rubro,))
        conn.commit()
        exito = True
    except sqlite3.IntegrityError:
        exito = False
    conn.close()
    return exito

def actualizar_rubro(rubro_id, nuevo_nombre):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE rubros SET nombre = ? WHERE id = ?", (nuevo_nombre, rubro_id))
        conn.commit()
        exito = True
    except sqlite3.IntegrityError:
        exito = False
    conn.close()
    return exito

def eliminar_rubro(rubro_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rubros WHERE id = ?", (rubro_id,))
    conn.commit()
    conn.close()

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

def agregar_medio_pago(nombre, tipo, detalle):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO medios_pago (nombre, tipo, detalle) VALUES (?, ?, ?)", (nombre, tipo, detalle))
        conn.commit()
        exito = True
    except sqlite3.IntegrityError:
        exito = False
    conn.close()
    return exito

def actualizar_medio_pago(mp_id, nombre, tipo, detalle):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE medios_pago SET nombre = ?, tipo = ?, detalle = ? WHERE id = ?
    """, (nombre, tipo, detalle, mp_id))
    conn.commit()
    conn.close()

def eliminar_medio_pago(mp_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medios_pago WHERE id = ?", (mp_id,))
    conn.commit()
    conn.close()

def get_pagos(proyecto_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM pagos WHERE proyecto_id = ?", conn, params=(proyecto_id,))
    conn.close()
    return df

def agregar_pago(proyecto_id, presupuesto_id, fecha, comprobante, tipo_gasto, medio_pago, cuotas, rubro, ambiente, proveedor, concepto, monto_ars, tipo_cambio):
    monto_usd = int(monto_ars / tipo_cambio) if tipo_cambio > 0 else 0
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
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

def actualizar_pago_completo(pago_id, presupuesto_id, fecha, comprobante, tipo_gasto, medio_pago, cuotas, rubro, ambiente, proveedor, concepto, monto_ars, tipo_cambio):
    monto_usd = int(monto_ars / tipo_cambio) if tipo_cambio > 0 else 0
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
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

# Funciones para Presupuesto
def get_presupuestos(proyecto_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM presupuestos_rubro WHERE proyecto_id = ?", conn, params=(proyecto_id,))
    conn.close()
    return df

def guardar_presupuesto_rubro(proyecto_id, rubro, ambiente, proveedor, concepto, moneda, monto_presupuestado):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO presupuestos_rubro (proyecto_id, rubro, ambiente, proveedor, concepto, moneda, monto_presupuestado) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (proyecto_id, rubro, ambiente, proveedor, concepto, moneda, int(monto_presupuestado)))
    conn.commit()
    conn.close()

def actualizar_presupuesto(ppto_id, rubro, ambiente, proveedor, concepto, moneda, monto_presupuestado):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
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

# Funciones para Especificaciones / Bitácora Técnica
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

# --- BARRA LATERAL: SELECCIÓN DE PROYECTO Y ACCESO ---
st.sidebar.header("🏢 Selector de Proyecto (ID)")
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
st.sidebar.header("🔐 Control de Perfil")
perfil = st.sidebar.selectbox("Perfil de Usuario", ["Project Manager (Admin)", "Inversora / Cliente"])

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

# Definición de Pestañas según el Perfil (Admin vs Cliente)
if perfil == "Project Manager (Admin)":
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "💳 Registro de Pagos", "📐 Especificaciones", "📊 Módulo de Reportes", 
        "🏢 ABM Proyectos", "📑 ABM Proveedores", "🛠️ ABM Rubros", 
        "💳 ABM Medios de Pago", "📋 ABM Presupuestos", "📈 Panel Financiero", "🚀 Escenarios Venta"
    ])
else:
    tab_cli_1, tab_cli_2, tab_cli_3, tab_cli_4 = st.tabs([
        "📐 Especificaciones", "📊 Módulo de Reportes", "📈 Panel Financiero", "🚀 Escenarios Venta"
    ])

# ==========================================
# MÓDULOS REPLICADOS (IDÉNTICOS PARA AMBOS PERFILES)
# ==========================================

def render_especificaciones_tab():
    st.subheader("📐 Especificaciones y Bitácora Técnica (Catálogo de Materiales)")
    st.info(f"Los materiales y productos comprados se incorporan automáticamente en la bitácora técnica de {proyecto_info['nombre']}.")
    
    df_esp_actual = get_especificaciones(proyecto_id_activo)
    if not df_esp_actual.empty:
        st.markdown('<p class="field-title">Filtrar Bitácora por Ambiente:</p>', unsafe_allow_html=True)
        filtro_amb_esp = st.selectbox("Filtrar Bitácora por Ambiente:", ["Todos"] + list(df_esp_actual["ambiente"].dropna().unique()), label_visibility="collapsed")
        df_esp_viz = df_esp_actual.copy()
        if filtro_amb_esp != "Todos":
            df_esp_viz = df_esp_viz[df_esp_viz["ambiente"] == filtro_amb_esp]
            
        df_esp_display = df_esp_viz[["id", "rubro", "ambiente", "proveedor", "producto_concepto", "detalles_tecnicos"]].copy()
        df_esp_display.columns = ["ID", "Rubro", "Ambiente", "Proveedor", "Concepto", "Detalles"]
        st.dataframe(df_esp_display, use_container_width=True)
        
        if perfil == "Project Manager (Admin)":
            st.markdown("### ✏️ Editar Detalle Técnico de un Producto")
            with st.form("form_editar_esp"):
                st.markdown('<p class="field-title">Seleccioná el ID de la especificación a editar</p>', unsafe_allow_html=True)
                ids_esp = df_esp_actual["id"].tolist()
                id_esp_sel = st.selectbox("Seleccioná el ID de la especificación a editar", ids_esp, label_visibility="collapsed")
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
    st.markdown("Tablero centralizado con la comparativa Presupuesto vs. Real, exposición por medios de pago, cash flow de cuotas y alertas de desvío.")
    
    rep_tab1, rep_tab2, rep_tab3, rep_tab4 = st.tabs([
        "📈 Presupuesto vs. Real", "💳 Exposición por Medio de Pago", "📅 Cash Flow de Cuotas", "🚨 Control de Desviaciones"
    ])
    
    # --- REPORTE 1: PRESUPUESTO VS REAL ---
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
                    "ID Ppto": row["id"],
                    "Rubro": row["rubro"],
                    "Ambiente": row["ambiente"],
                    "Proveedor": row["proveedor"],
                    "Concepto": row["concepto"],
                    "Moneda Ppto": moneda_ppto,
                    "Ppto (ARS)": ppto_ars,
                    "Ppto (USD)": ppto_usd,
                    "Ejec (ARS)": ejec_ars,
                    "Ejec (USD)": ejec_usd,
                    "Saldo (ARS)": saldo_ars,
                    "Saldo (USD)": saldo_usd
                })
                
            if not df_pagos_rep.empty:
                pagos_libres = df_pagos_rep[df_pagos_rep["presupuesto_id"].isnull() | (df_pagos_rep["presupuesto_id"] == 0)]
                if not pagos_libres.empty:
                    libres_ars = int(pagos_libres["monto_ars"].sum())
                    libres_usd = int(pagos_libres["monto_usd"].sum())
                    lista_filas.append({
                        "ID Ppto": "LIBRE",
                        "Rubro": "Gastos Sin Presupuesto",
                        "Ambiente": "General",
                        "Proveedor": "Varios",
                        "Concepto": "Erogaciones Libres / Directas",
                        "Moneda Ppto": "ARS",
                        "Ppto (ARS)": 0,
                        "Ppto (USD)": 0,
                        "Ejec (ARS)": libres_ars,
                        "Ejec (USD)": libres_usd,
                        "Saldo (ARS)": -libres_ars,
                        "Saldo (USD)": -libres_usd
                    })
                    
            df_final_rep = pd.DataFrame(lista_filas)
            
            total_p_ars = int(df_ppto_rep.apply(lambda r: r["monto_presupuestado"] if r["moneda"] == "ARS" else r["monto_presupuestado"] * tc_ref, axis=1).sum())
            total_p_usd = int(df_ppto_rep.apply(lambda r: r["monto_presupuestado"] if r["moneda"] == "USD" else int(r["monto_presupuestado"] / tc_ref), axis=1).sum())
            total_e_ars = int(df_pagos_rep["monto_ars"].sum()) if not df_pagos_rep.empty else 0
            total_e_usd = int(df_pagos_rep["monto_usd"].sum()) if not df_pagos_rep.empty else 0
            
            st.markdown("#### 💰 Totales Generales Globales Bimonetarios")
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
            st.markdown("#### 📋 Detalle Partida por Partida (Bimonetario)")
            df_viz = df_final_rep.copy()
            for col in ["Ppto (ARS)", "Ppto (USD)", "Ejec (ARS)", "Ejec (USD)", "Saldo (ARS)", "Saldo (USD)"]:
                df_viz[col] = df_viz[col].apply(lambda x: f"${int(x):,}".replace(",", "."))
            st.dataframe(df_viz, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 📑 Totales Consolidados por Rubro y por Ambiente")
            st.markdown('<p class="field-title">Agrupar totales por:</p>', unsafe_allow_html=True)
            tipo_agrupacion = st.radio("Agrupar totales por:", ["Rubro de Obra", "Ambiente"], horizontal=True, label_visibility="collapsed")
            col_agruppar = "Rubro" if tipo_agrupacion == "Rubro de Obra" else "Ambiente"
            
            df_agrupado = df_final_rep.groupby(col_agruppar)[["Ppto (ARS)", "Ppto (USD)", "Ejec (ARS)", "Ejec (USD)", "Saldo (ARS)", "Saldo (USD)"]].sum().reset_index()
            df_agr_viz = df_agrupado.copy()
            for col in ["Ppto (ARS)", "Ppto (USD)", "Ejec (ARS)", "Ejec (USD)", "Saldo (ARS)", "Saldo (USD)"]:
                df_agr_viz[col] = df_agr_viz[col].apply(lambda x: f"${int(x):,}".replace(",", "."))
            st.dataframe(df_agr_viz, use_container_width=True)
        else:
            st.info("No hay presupuestos cargados para este proyecto.")

    # --- REPORTE 2: EXPOSICIÓN POR MEDIO DE PAGO ---
    with rep_tab2:
        st.markdown("### 💳 Exposición Consolidada por Medio de Pago / Tarjeta")
        df_pagos_rep = get_pagos(proyecto_id_activo)
        if not df_pagos_rep.empty:
            df_mp_resumen = df_pagos_rep.groupby("medio_pago").agg(
                total_ars=("monto_ars", "sum"),
                total_usd=("monto_usd", "sum"),
                cantidad_pagos=("id", "count"),
                cuotas_promedio=("cuotas", "mean")
            ).reset_index()
            
            df_mp_viz = df_mp_resumen.copy()
            df_mp_viz["total_ars"] = df_mp_viz["total_ars"].apply(lambda x: f"${int(x):,}".replace(",", "."))
            df_mp_viz["total_usd"] = df_mp_viz["total_usd"].apply(lambda x: f"${int(x):,}".replace(",", "."))
            df_mp_viz["cuotas_promedio"] = df_mp_viz["cuotas_promedio"].apply(lambda x: f"{round(x, 1)}")
            df_mp_viz.columns = ["Medio de Pago", "Total (ARS)", "Total (USD)", "Cant. Pagos", "Prom. Cuotas"]
            st.dataframe(df_mp_viz, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 🔍 Detalle de Transacciones por Medio de Pago")
            st.markdown('<p class="field-title">Seleccioná un medio de pago para auditar</p>', unsafe_allow_html=True)
            lista_medios_utilizados = df_pagos_rep["medio_pago"].unique().tolist()
            medio_seleccionado = st.selectbox("Seleccioná un medio de pago para auditar", lista_medios_utilizados, label_visibility="collapsed")
            
            df_filtrado_mp = df_pagos_rep[df_pagos_rep["medio_pago"] == medio_seleccionado]
            sub_ars = int(df_filtrado_mp["monto_ars"].sum())
            sub_usd = int(df_filtrado_mp["monto_usd"].sum())
            
            m_c1, m_c2 = st.columns(2)
            with m_c1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total con {medio_seleccionado} (ARS)</div>
                        <div class="metric-value">${sub_ars:,} ARS</div>
                    </div>
                """.replace(",", "."), unsafe_allow_html=True)
            with m_c2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total con {medio_seleccionado} (USD)</div>
                        <div class="metric-value">${sub_usd:,} USD</div>
                    </div>
                """.replace(",", "."), unsafe_allow_html=True)
                
            df_filtrado_display = df_filtrado_mp[["id", "fecha", "comprobante", "rubro", "ambiente", "proveedor", "concepto", "cuotas", "monto_ars", "monto_usd"]].copy()
            df_filtrado_display["monto_ars"] = df_filtrado_display["monto_ars"].apply(lambda x: f"${int(x):,}".replace(",", "."))
            df_filtrado_display["monto_usd"] = df_filtrado_display["monto_usd"].apply(lambda x: f"${int(x):,}".replace(",", "."))
            df_filtrado_display.columns = ["ID", "Fecha", "Comprobante", "Rubro", "Ambiente", "Proveedor", "Concepto", "Cuotas", "Monto (ARS)", "Monto (USD)"]
            st.dataframe(df_filtrado_display, use_container_width=True)
        else:
            st.info("No hay pagos registrados para analizar.")

    # --- REPORTE 3: CASH FLOW DE CUOTAS ---
    with rep_tab3:
        st.markdown("### 📅 Proyección de Cash Flow y Vencimientos de Cuotas")
        df_pagos_rep = get_pagos(proyecto_id_activo)
        if not df_pagos_rep.empty:
            df_cuotas_calc = df_pagos_rep.copy()
            df_cuotas_calc["monto_cuota_ars"] = df_cuotas_calc.apply(lambda r: int(r["monto_ars"] / r["cuotas"]) if r["cuotas"] > 0 else r["monto_ars"], axis=1)
            df_cuotas_calc["monto_cuota_usd"] = df_cuotas_calc.apply(lambda r: int(r["monto_usd"] / r["cuotas"]) if r["cuotas"] > 0 else r["monto_usd"], axis=1)
            
            df_cuotas_display = df_cuotas_calc[["id", "fecha", "medio_pago", "proveedor", "concepto", "cuotas", "monto_ars", "monto_cuota_ars", "monto_usd", "monto_cuota_usd"]].copy()
            df_cuotas_display["monto_ars"] = df_cuotas_display["monto_ars"].apply(lambda x: f"${int(x):,}".replace(",", "."))
            df_cuotas_display["monto_cuota_ars"] = df_cuotas_display["monto_cuota_ars"].apply(lambda x: f"${int(x):,}".replace(",", "."))
            df_cuotas_display["monto_usd"] = df_cuotas_display["monto_usd"].apply(lambda x: f"${int(x):,}".replace(",", "."))
            df_cuotas_display["monto_cuota_usd"] = df_cuotas_display["monto_cuota_usd"].apply(lambda x: f"${int(x):,}".replace(",", "."))
            
            df_cuotas_display.columns = ["ID", "Fecha", "Medio Pago", "Proveedor", "Concepto", "Cuotas", "Total (ARS)", "Cuota (ARS)", "Total (USD)", "Cuota (USD)"]
            st.dataframe(df_cuotas_display, use_container_width=True)
        else:
            st.info("No hay pagos registrados para proyectar cuotas.")

    # --- REPORTE 4: CONTROL DE DESVIACIONES ---
    with rep_tab4:
        st.markdown("### 🚨 Control de Desviaciones por Partida (Alerta Temprana)")
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
                    "ID": row["id"],
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
    st.markdown("Distribución gráfica de erogaciones reales por **Rubro de Obra** y **Ambiente** (con sus porcentajes de incidencia), acompañadas de la tabla consolidada bimonetaria completa.")
    
    df_pagos_fin = get_pagos(proyecto_id_activo)
    if not df_pagos_fin.empty:
        fin_tab_rubro, fin_tab_ambiente = st.tabs([
            "📂 Distribución por Rubro", "🏠 Distribución por Ambiente"
        ])
        
        colores_pasteles = ["#94B3FD", "#B9E4C9", "#FCE38A", "#F38181", "#E2D7F7", "#FFD166", "#A0C4FF", "#CAFFBF"]
        
        # --- 1. DISTRIBUCIÓN POR RUBRO ---
        with fin_tab_rubro:
            st.markdown("### 📂 Análisis de Gastos por Rubro de Obra")
            df_rubro_agg = df_pagos_fin.groupby("rubro")[["monto_usd", "monto_ars"]].sum().reset_index()
            total_usd_gen = df_rubro_agg["monto_usd"].sum()
            df_rubro_agg["porcentaje"] = ((df_rubro_agg["monto_usd"] / total_usd_gen) * 100).round(1)
            
            col_r1, col_r2 = st.columns([1.3, 0.9])
            with col_r1:
                fig_rubro = px.pie(df_rubro_agg, values="monto_usd", names="rubro", title=f"Participación por Rubro (USD) - {proyecto_info['nombre']}", hole=0.4, color_discrete_sequence=colores_pasteles)
                fig_rubro.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="sans-serif", color="#2d3748"))
                st.plotly_chart(fig_rubro, use_container_width=True)
            with col_r2:
                st.markdown('<div style="margin-top: 45px;"><p style="color:#3182ce; font-weight:400; font-size:13px; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:12px;">📌 Referencia y %</p></div>', unsafe_allow_html=True)
                for idx, row in df_rubro_agg.iterrows():
                    st.markdown(f"<span style='font-size:13px; color:#4a5568;'><b>{row['rubro']}</b>:<br>🔹 <b>{row['porcentaje']}%</b> (${int(row['monto_usd']):,} USD)</span><br><br>", unsafe_allow_html=True)
                    
            st.markdown("---")
            st.markdown("#### 📋 Detalle Consolidado Bimonetario por Rubro")
            total_rubro_usd = df_rubro_agg["monto_usd"].sum()
            total_rubro_ars = df_rubro_agg["monto_ars"].sum()
            
            df_rubro_table = df_rubro_agg[["rubro", "monto_usd", "monto_ars", "porcentaje"]].copy()
            df_rubro_table["monto_usd"] = df_rubro_table["monto_usd"].apply(lambda x: f"${int(x):,} USD".replace(",", "."))
            df_rubro_table["monto_ars"] = df_rubro_table["monto_ars"].apply(lambda x: f"${int(x):,} ARS".replace(",", "."))
            df_rubro_table["porcentaje"] = df_rubro_table["porcentaje"].apply(lambda x: f"{x}%")
            df_rubro_table.columns = ["Rubro de Obra", "Total (USD)", "Total (ARS)", "% del Total"]
            st.dataframe(df_rubro_table, use_container_width=True)
            st.markdown(f"**TOTALES GENERALES:** 💵 **${int(total_rubro_ars):,} ARS** | 💲 **${int(total_rubro_usd):,} USD**".replace(",", "."), unsafe_allow_html=True)
            
        # --- 2. DISTRIBUCIÓN POR AMBIENTE ---
        with fin_tab_ambiente:
            st.markdown("### 🏠 Análisis de Gastos por Ambiente")
            df_amb_agg = df_pagos_fin.groupby("ambiente")[["monto_usd", "monto_ars"]].sum().reset_index()
            total_usd_amb = df_amb_agg["monto_usd"].sum()
            df_amb_agg["porcentaje"] = ((df_amb_agg["monto_usd"] / total_usd_amb) * 100).round(1)
            
            col_a1, col_a2 = st.columns([1.3, 0.9])
            with col_a1:
                fig_amb = px.pie(df_amb_agg, values="monto_usd", names="ambiente", title=f"Participación por Ambiente (USD) - {proyecto_info['nombre']}", hole=0.4, color_discrete_sequence=colores_pasteles)
                fig_amb.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="sans-serif", color="#2d3748"))
                st.plotly_chart(fig_amb, use_container_width=True)
            with col_a2:
                st.markdown('<div style="margin-top: 45px;"><p style="color:#3182ce; font-weight:400; font-size:13px; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:12px;">📌 Referencia y %</p></div>', unsafe_allow_html=True)
                for idx, row in df_amb_agg.iterrows():
                    st.markdown(f"<span style='font-size:13px; color:#4a5568;'><b>{row['ambiente']}</b>:<br>🔹 <b>{row['porcentaje']}%</b> (${int(row['monto_usd']):,} USD)</span><br><br>", unsafe_allow_html=True)
                    
            st.markdown("---")
            st.markdown("#### 📋 Detalle Consolidado Bimonetario por Ambiente")
            total_amb_usd = df_amb_agg["monto_usd"].sum()
            total_amb_ars = df_amb_agg["monto_ars"].sum()
            
            df_amb_table = df_amb_agg[["ambiente", "monto_usd", "monto_ars", "porcentaje"]].copy()
            df_amb_table["monto_usd"] = df_amb_table["monto_usd"].apply(lambda x: f"${int(x):,} USD".replace(",", "."))
            df_amb_table["monto_ars"] = df_amb_table["monto_ars"].apply(lambda x: f"${int(x):,} ARS".replace(",", "."))
            df_amb_table["porcentaje"] = df_amb_table["porcentaje"].apply(lambda x: f"{x}%")
            df_amb_table.columns = ["Ambiente", "Total (USD)", "Total (ARS)", "% del Total"]
            st.dataframe(df_amb_table, use_container_width=True)
            st.markdown(f"**TOTALES GENERALES:** 💵 **${int(total_amb_ars):,} ARS** | 💲 **${int(total_amb_usd):,} USD**".replace(",", "."), unsafe_allow_html=True)
    else:
        st.info("Carga pagos para visualizar los gráficos y porcentajes.")

def render_escenarios_venta():
    st.subheader("🚀 Modelado de Escenarios de Venta, Mercado y Viabilidad Financiera")
    st.markdown("Simulador profesional: Hereda superficie y compra del ABM, permite ajustar la remodelación, el mantenimiento, ingresar referencia de mercado y los precios de venta por m² o total.")
    
    sup_m2 = float(sup_total)
    precio_compra_base = int(precio_compra_proy)
    gastos_compra = int(precio_compra_base * 0.08)
    
    st.markdown("---")
    st.markdown("### ⚙️ Parámetros y Ajustes de Escenario")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        st.markdown(f'Superficie Total (m²): {sup_m2} m²', unsafe_allow_html=True)
        st.markdown(f"**Compra Base:** ${precio_compra_base:,} USD".replace(",", "."))
        st.markdown(f"**Gastos de Compra (8%):** ${gastos_compra:,} USD".replace(",", "."))
    with col_p2:
        st.markdown('🛠️ Valor Remodelación (USD)', unsafe_allow_html=True)
        remodelacion_input = st.number_input("Remodelación Escenario", min_value=0, value=int(presupuesto_ref), step=5000, format="%d", label_visibility="collapsed")
    with col_p3:
        st.markdown('🏠 Gastos Mantenimiento (USD)', unsafe_allow_html=True)
        mantenimiento_input = st.number_input("Gastos Mantenimiento", min_value=0, value=5000, step=1000, format="%d", label_visibility="collapsed")
    with col_p4:
        st.markdown('📊 Referencia Valor de Mercado', unsafe_allow_html=True)
        tipo_ref_mercado = st.radio("Ref Mercado", ["Valor por m² (USD/m²)", "Valor Total (USD)"], horizontal=True, label_visibility="collapsed")
        
    col_m1, col_m2 = st.columns(2)
    if tipo_ref_mercado == "Valor por m² (USD/m²)":
        with col_m1:
            val_m2_mercado = st.number_input("💵 Valor de Mercado por m² (USD/m²)", min_value=500, value=3800, step=100, format="%d")
            val_mercado_total = int(val_m2_mercado * sup_m2)
        with col_m2:
            st.markdown(f"**Valor Mercado Total Equivalente:**<br><span style='font-size: 15px; font-weight: 600; color: #1a202c;'>${val_mercado_total:,} USD</span>".replace(",", "."), unsafe_allow_html=True)
    else:
        with col_m1:
            val_mercado_total = st.number_input("💵 Valor de Mercado Total (USD)", min_value=50000, value=520000, step=10000, format="%d")
        with col_m2:
            val_m2_mercado = int(val_mercado_total / sup_m2) if sup_m2 > 0 else 0
            st.markdown(f"**Valor Equivalente por m²:**<br><br>${val_m2_mercado:,} USD/m²".replace(",", "."), unsafe_allow_html=True)
            
    st.markdown("---")
    st.markdown("### 📈 Ingreso Manual de Precios de Venta Estimados (por Escenario)")
    modo_ingreso_vta = st.radio("Modo de ingreso para los precios de venta:", ["Ingresar por Valor m² (USD/m²)", "Ingresar por Valor Total (USD)"], horizontal=True)
    
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown("#### 📉 Escenario Pesimista")
        if modo_ingreso_vta == "Ingresar por Valor m² (USD/m²)":
            pes_m2_input = st.number_input("Pesimista (USD/m²)", min_value=500, value=val_m2_mercado, step=100, format="%d")
            pes_vta = int(pes_m2_input * sup_m2)
        else:
            pes_vta = st.number_input("Pesimista Total (USD)", min_value=50000, value=val_mercado_total, step=10000, format="%d")
            pes_m2_input = int(pes_vta / sup_m2) if sup_m2 > 0 else 0
        st.markdown(f"📌 Equivalente: <b>{pes_m2_input:,} USD/m²</b> | Total: <b>{pes_vta:,} USD</b>".replace(",", "."), unsafe_allow_html=True)
        
    with sc2:
        st.markdown("#### 📊 Escenario Conservador")
        if modo_ingreso_vta == "Ingresar por Valor m² (USD/m²)":
            con_m2_input = st.number_input("Conservador (USD/m²)", min_value=500, value=int(val_m2_mercado * 1.12), step=100, format="%d")
            con_vta = int(con_m2_input * sup_m2)
        else:
            con_vta = st.number_input("Conservador Total (USD)", min_value=50000, value=int(val_mercado_total * 1.12), step=10000, format="%d")
            con_m2_input = int(con_vta / sup_m2) if sup_m2 > 0 else 0
        st.markdown(f"📌 Equivalente: <b>{con_m2_input:,} USD/m²</b> | Total: <b>{con_vta:,} USD</b>".replace(",", "."), unsafe_allow_html=True)
        
    with sc3:
        st.markdown("#### 🚀 Escenario Optimista")
        if modo_ingreso_vta == "Ingresar por Valor m² (USD/m²)":
            opt_m2_input = st.number_input("Optimista (USD/m²)", min_value=500, value=int(val_m2_mercado * 1.25), step=100, format="%d")
            opt_vta = int(opt_m2_input * sup_m2)
        else:
            opt_vta = st.number_input("Optimista Total (USD)", min_value=50000, value=int(val_mercado_total * 1.25), step=10000, format="%d")
            opt_m2_input = int(opt_vta / sup_m2) if sup_m2 > 0 else 0
        st.markdown(f"📌 Equivalente: <b>{opt_m2_input:,} USD/m²</b> | Total: <b>{opt_vta:,} USD</b>".replace(",", "."), unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("### 💰 Resultados de Rentabilidad y Alertas Automáticas de Viabilidad")
    
    costo_inversion_total = (precio_compra_base + gastos_compra + remodelacion_input + mantenimiento_input)
    
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
    
    def mostrar_tabla_escenario(titulo, gventa, profit, roi, dif, tipo_alerta, texto_alerta, v_venta, v_compra, g_compra, v_remodelacion, g_mantenimiento):
        st.markdown(f"#### {titulo}")
        df_tabla_esc = pd.DataFrame({
            "Indicador Financiero": ["Valor de Venta", "Valor de Compra", "Gastos de Compra (8%)", "Remodelación", "Gastos Mantenimiento", "Gastos de Venta (6%)", "Ganancia Total (USD)", "ROI Neto", "Dif. Mercado"],
            "Valor del Escenario": [
                f"${v_venta:,} USD".replace(",", "."), f"${v_compra:,} USD".replace(",", "."), f"${g_compra:,} USD".replace(",", "."), 
                f"${v_remodelacion:,} USD".replace(",", "."), f"${g_mantenimiento:,} USD".replace(",", "."), f"${gventa:,} USD".replace(",", "."), 
                f"${profit:,} USD".replace(",", "."), f"{roi}%", f"{round(dif, 1)}%"
            ]
        })
        st.dataframe(df_tabla_esc, use_container_width=True, hide_index=True)
        if tipo_alerta == "error":
            st.error(texto_alerta)
        elif tipo_alerta == "warning":
            st.warning(texto_alerta)
        else:
            st.success(texto_alerta)
            
    with res1:
        if pes_profit < 0:
            alerta_tipo_p = "error"
            alerta_texto_p = "🚨 **ALERTA ROJA:** Proyecto NO VIABLE (Profit Negativo). Pérdida patrimonial."
        elif pes_roi < 10:
            alerta_tipo_p = "warning"
            alerta_texto_p = "⚠️ **ALERTA AMARILLA:** Margen ajustado (< 10%). Riesgo operativo."
        else:
            alerta_tipo_p = "success"
            alerta_texto_p = "🟢 Viable con margen moderado."
        mostrar_tabla_escenario("📉 Resultado Pesimista", pes_gventa, pes_profit, pes_roi, pes_dif, alerta_tipo_p, alerta_texto_p, pes_vta, precio_compra_base, gastos_compra, remodelacion_input, mantenimiento_input)
        
    with res2:
        if con_profit < 0:
            alerta_tipo_c = "error"
            alerta_texto_c = "🚨 **ALERTA ROJA:** No viable en conservador."
        elif con_roi < 15:
            alerta_tipo_c = "warning"
            alerta_texto_c = "🟡 **ALERTA AMARILLA:** Rentabilidad moderada (10% - 15%)."
        else:
            alerta_tipo_c = "success"
            alerta_texto_c = "🟢 Escenario saludable y seguro."
        mostrar_tabla_escenario("📊 Resultado Conservador", con_gventa, con_profit, con_roi, con_dif, alerta_tipo_c, alerta_texto_c, con_vta, precio_compra_base, gastos_compra, remodelacion_input, mantenimiento_input)
        
    with res3:
        if opt_profit < 0:
            alerta_tipo_o = "error"
            alerta_texto_o = "🚨 **ALERTA ROJA:** No viable."
        else:
            alerta_tipo_o = "success"
            alerta_texto_o = "🟢 **EXCELENTE:** Alta rentabilidad (Diferencial superior sobre mercado)."
        mostrar_tabla_escenario("🚀 Resultado Optimista", opt_gventa, opt_profit, opt_roi, opt_dif, alerta_tipo_o, alerta_texto_o, opt_vta, precio_compra_base, gastos_compra, remodelacion_input, mantenimiento_input)
        
    st.markdown("---")
    st.markdown("### 📐 Referencia de Fórmulas y Metodología Financiera Utilizadas")
    st.markdown("""
    * **Gastos de Compra (8%):** Precio de Compra (ABM) × 0.08
    * **Costo Total de Inversión:** Precio de Compra + Gastos de Compra + Remodelación + Gastos de Mantenimiento
    * **Gastos de Venta (6%):** Valor de Venta Ingresado × 0.06
    * **Ganancia Total (Profit Neto):** Valor de Venta Ingresado - (Costo Total de Inversión + Gastos de Venta)
    * **ROI Neto (%):** (Ganancia Total / Costo Total de Inversión) × 100
    * **Diferencia de Mercado (%):** [(Valor de Venta Ingresado - Valor de Mercado Total) / Valor de Mercado Total] × 100
    """, unsafe_allow_html=True)

# ==========================================
# RENDERIZADO DE VISTAS (ADMIN VS CLIENTE)
# ==========================================
if perfil == "Project Manager (Admin)":
    with tab1:
        st.subheader("➕ Cargar Nuevo Gasto / Pago")
        df_ppto_disponibles = get_presupuestos(proyecto_id_activo)
        ppto_opciones = {"Sin asociar (Gasto libre)": None}
        if not df_ppto_disponibles.empty:
            for idx, row in df_ppto_disponibles.iterrows():
                label_ppto = f"ID {row['id']} | Rubro: {row['rubro']} | Amb: {row['ambiente']} | Prov: {row['proveedor']} | Tarea: {row['concepto']} ({row['monto_presupuestado']:,} {row['moneda']})"
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
                ambiente_sel = st.selectbox("Ambiente", ["Cocina", "Baño 1", "Baño 2", "Toilette", "Living y Pasillos", "Balcón", "General"], label_visibility="collapsed")
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
        st.subheader("📋 Historial Completo de Erogaciones, Totales y Edición / Eliminación")
        df_pagos_actual = get_pagos(proyecto_id_activo)
        
        if not df_pagos_actual.empty:
            total_ars_acumulado = int(df_pagos_actual["monto_ars"].sum())
            total_usd_acumulado = int(df_pagos_actual["monto_usd"].sum())
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Ejecutado en Pesos</div>
                        <div class="metric-value">${total_ars_acumulado:,} ARS</div>
                    </div>
                """.replace(",", "."), unsafe_allow_html=True)
            with t_col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Ejecutado en Dólares</div>
                        <div class="metric-value">${total_usd_acumulado:,} USD</div>
                    </div>
                """.replace(",", "."), unsafe_allow_html=True)
                
            st.markdown("---")
            df_display = df_pagos_actual.copy()
            df_display["monto_ars"] = df_display["monto_ars"].apply(lambda x: f"{int(x):,}".replace(",", "."))
            df_display["tipo_cambio"] = df_display["tipo_cambio"].apply(lambda x: f"{int(x):,}".replace(",", "."))
            df_display["monto_usd"] = df_display["monto_usd"].apply(lambda x: f"{int(x):,}".replace(",", "."))
            df_display.columns = ["ID", "Proj ID", "Ppto ID", "Fecha", "Comprobante", "Tipo Gasto", "Medio Pago", "Cuotas", "Rubro", "Ambiente", "Proveedor", "Concepto", "Monto (ARS)", "TC", "Monto (USD)"]
            st.dataframe(df_display, use_container_width=True)
            
            st.markdown("### ✏️ Modificar o Eliminar un Registro de Pago")
            ids_disponibles = df_pagos_actual["id"].tolist()
            st.markdown('<p class="field-title">Seleccioná el ID del pago a editar o borrar</p>', unsafe_allow_html=True)
            id_a_gestionar = st.selectbox("Seleccioná el ID del pago a editar o borrar", ids_disponibles, label_visibility="collapsed")
            reg_sel = df_pagos_actual[df_pagos_actual["id"] == id_a_gestionar].iloc[0]
            
            with st.form("form_editar_pago"):
                st.markdown(f"**Editando Registro ID: {id_a_gestionar}**")
                st.markdown('<p class="field-title">Vincular con Presupuesto</p>', unsafe_allow_html=True)
                e_asoc_edit = st.selectbox("Vincular con Presupuesto", list(ppto_opciones.keys()), index=0, label_visibility="collapsed")
                e_ppto_id = ppto_opciones[e_asoc_edit]
                
                e_c0, e_ca, e_cmp, e_ccuotas = st.columns(4)
                with e_c0:
                    st.markdown('<p class="field-title">Tipo Gasto</p>', unsafe_allow_html=True)
                    e_tipo_gasto = st.selectbox("Tipo Gasto", ["Material / Producto", "Servicio"], index=0 if reg_sel.get("tipo_gasto") == "Material / Producto" else 1, label_visibility="collapsed")
                with e_ca:
                    st.markdown('<p class="field-title">Comprobante</p>', unsafe_allow_html=True)
                    e_comprobante = st.text_input("Comprobante", value=str(reg_sel.get("comprobante", "")), label_visibility="collapsed")
                medios_disponibles = get_medios_pago()
                val_medio = reg_sel.get("medio_pago", medios_disponibles[0])
                idx_medio = medios_disponibles.index(val_medio) if val_medio in medios_disponibles else 0
                with e_cmp:
                    st.markdown('<p class="field-title">Medio Pago</p>', unsafe_allow_html=True)
                    e_medio_pago = st.selectbox("Medio Pago", medios_disponibles, index=idx_medio, label_visibility="collapsed")
                with e_ccuotas:
                    st.markdown('<p class="field-title">Cuotas</p>', unsafe_allow_html=True)
                    e_cuotas = st.number_input("Cuotas", value=int(reg_sel.get("cuotas", 1)), min_value=1, step=1, format="%d", label_visibility="collapsed")
                    
                e_col1, e_col2, e_col3 = st.columns(3)
                with e_col1:
                    st.markdown('<p class="field-title">Fecha (YYYY-MM-DD)</p>', unsafe_allow_html=True)
                    e_fecha = st.text_input("Fecha (YYYY-MM-DD)", value=reg_sel["fecha"], label_visibility="collapsed")
                with e_col2:
                    st.markdown('<p class="field-title">Rubro</p>', unsafe_allow_html=True)
                    e_rubro = st.selectbox("Rubro", get_rubros(), index=get_rubros().index(reg_sel["rubro"]) if reg_sel["rubro"] in get_rubros() else 0, label_visibility="collapsed")
                with e_col3:
                    st.markdown('<p class="field-title">Ambiente</p>', unsafe_allow_html=True)
                    amb_list = ["Cocina", "Baño 1", "Baño 2", "Toilette", "Living y Pasillos", "Balcón", "General"]
                    e_ambiente = st.selectbox("Ambiente", amb_list, index=amb_list.index(reg_sel["ambiente"]) if reg_sel["ambiente"] in amb_list else 0, label_visibility="collapsed")
                    
                e_col4, e_col5, e_col6 = st.columns(3)
                with e_col4:
                    st.markdown('<p class="field-title">Proveedor</p>', unsafe_allow_html=True)
                    e_proveedor = st.selectbox("Proveedor", get_proveedores(), index=get_proveedores().index(reg_sel["proveedor"]) if reg_sel["proveedor"] in get_proveedores() else 0, label_visibility="collapsed")
                with e_col5:
                    st.markdown('<p class="field-title">Concepto</p>', unsafe_allow_html=True)
                    e_concepto = st.text_input("Concepto", value=reg_sel["concepto"], label_visibility="collapsed")
                with e_col6:
                    st.markdown('<p class="field-title">Monto ARS</p>', unsafe_allow_html=True)
                    e_monto = st.number_input("Monto ARS", value=int(reg_sel["monto_ars"]), step=10000, format="%d", label_visibility="collapsed")
                    
                st.markdown('<p class="field-title">Tipo de Cambio</p>', unsafe_allow_html=True)
                e_tc = st.number_input("Tipo de Cambio", value=int(reg_sel["tipo_cambio"]) if reg_sel["tipo_cambio"] > 0 else 1250, step=10, format="%d", label_visibility="collapsed")
                
                btn_modificar = st.form_submit_button("🔄 Actualizar Todos los Datos")
                btn_eliminar = st.form_submit_button("🗑️ Eliminar este Pago")
                
                if btn_modificar:
                    actualizar_pago_completo(id_a_gestionar, e_ppto_id, e_fecha, e_comprobante, e_tipo_gasto, e_medio_pago, e_cuotas, e_rubro, e_ambiente, e_proveedor, e_concepto, e_monto, e_tc)
                    st.success("¡Registro actualizado con éxito!")
                    st.rerun()
                if btn_eliminar:
                    eliminar_pago(id_a_gestionar)
                    st.success("¡Pago eliminado correctamente!")
                    st.rerun()
        else:
            st.info("No hay pagos cargados para este proyecto todavía.")

    with tab2:
        render_especificaciones_tab()
    with tab3:
        render_reportes_tab()
    with tab4:
        st.subheader("🏢 ABM de Proyectos y Clientes / Inversores")
        with st.form("form_nuevo_proyecto", clear_on_submit=True):
            st.markdown('<p class="field-title">Nombre del Proyecto (ej. Libertador 4000)</p>', unsafe_allow_html=True)
            np_nombre = st.text_input("Nombre del Proyecto (ej. Libertador 4000)", label_visibility="collapsed")
            st.markdown('<p class="field-title">Nombre del Cliente / Inversor (ej. Jesica)</p>', unsafe_allow_html=True)
            np_cliente = st.text_input("Nombre del Cliente / Inversor (ej. Jesica)", label_visibility="collapsed")
            st.markdown('<p class="field-title">Superficie Total (m²)</p>', unsafe_allow_html=True)
            np_sup = st.number_input("Superficie Total (m²)", min_value=10, value=100, step=1, format="%d", label_visibility="collapsed")
            st.markdown('<p class="field-title">Precio de Compra Inmueble (USD)</p>', unsafe_allow_html=True)
            np_compra = st.number_input("Precio de Compra Inmueble (USD)", min_value=10000, value=250000, step=10000, format="%d", label_visibility="collapsed")
            st.markdown('<p class="field-title">Presupuesto Reforma (USD)</p>', unsafe_allow_html=True)
            np_ref = st.number_input("Presupuesto Reforma (USD)", min_value=1000, value=50000, step=5000, format="%d", label_visibility="collapsed")
            st.markdown('<p class="field-title">Precio Objetivo Venta (USD)</p>', unsafe_allow_html=True)
            np_salida = st.number_input("Precio Objetivo Venta (USD)", min_value=10000, value=350000, step=10000, format="%d", label_visibility="collapsed")
            
            if st.form_submit_button("➕ Crear Nuevo Proyecto"):
                if np_nombre and np_cliente:
                    if agregar_proyecto(np_nombre, np_cliente, np_sup, np_compra, np_ref, np_salida):
                        st.success(f"¡Proyecto '{np_nombre}' creado con éxito para {np_cliente}!")
                        st.rerun()
                    else:
                        st.error("El nombre del proyecto ya existe.")
                else:
                    st.warning("Completá el nombre y el cliente.")
                    
        st.markdown("---")
        st.subheader("📋 Proyectos Registrados (Modificar / Eliminar)")
        df_proy_viz = get_proyectos()
        df_proy_display = df_proy_viz.copy()
        df_proy_display.columns = ["ID", "Nombre del Proyecto", "Cliente", "Superficie (m²)", "Compra (USD)", "Reforma (USD)", "Venta (USD)"]
        st.dataframe(df_proy_display, use_container_width=True)
        
        if not df_proy_viz.empty:
            st.markdown('<p class="field-title">Seleccionar ID de Proyecto a Modificar/Eliminar</p>', unsafe_allow_html=True)
            id_proy_sel = st.selectbox("Seleccionar ID de Proyecto a Modificar/Eliminar", df_proy_viz["id"].tolist(), label_visibility="collapsed")
            reg_proy = df_proy_viz[df_proy_viz["id"] == id_proy_sel].iloc[0]
            
            with st.form("form_editar_proyecto"):
                st.markdown(f"**Editando Proyecto ID: {id_proy_sel}**")
                st.markdown('<p class="field-title">Nombre del Proyecto</p>', unsafe_allow_html=True)
                ed_p_nombre = st.text_input("Nombre", value=reg_proy["nombre"], label_visibility="collapsed")
                st.markdown('<p class="field-title">Nombre del Cliente / Inversor</p>', unsafe_allow_html=True)
                ed_p_cliente = st.text_input("Cliente", value=reg_proy["cliente"], label_visibility="collapsed")
                st.markdown('<p class="field-title">Superficie Total (m²)</p>', unsafe_allow_html=True)
                ed_p_sup = st.number_input("Superficie (m²)", value=float(reg_proy["superficie_total"]), step=1.0, label_visibility="collapsed")
                st.markdown('<p class="field-title">Precio de Compra Inmueble (USD)</p>', unsafe_allow_html=True)
                ed_p_compra = st.number_input("Precio Compra (USD)", value=int(reg_proy["precio_compra"]), step=5000, label_visibility="collapsed")
                st.markdown('<p class="field-title">Presupuesto Reforma (USD)</p>', unsafe_allow_html=True)
                ed_p_ref = st.number_input("Presupuesto Reforma (USD)", value=int(reg_proy["presupuesto_reforma"]), step=2000, label_visibility="collapsed")
                st.markdown('<p class="field-title">Precio Objetivo Venta (USD)</p>', unsafe_allow_html=True)
                ed_p_venta = st.number_input("Precio Objetivo Venta (USD)", value=int(reg_proy["precio_objetivo"]), step=5000, label_visibility="collapsed")
                
                btn_act_proy = st.form_submit_button("🔄 Actualizar Proyecto")
                btn_del_proy = st.form_submit_button("🗑️ Eliminar Proyecto")
                
                if btn_act_proy:
                    actualizar_proyecto(id_proy_sel, ed_p_nombre, ed_p_cliente, ed_p_sup, ed_p_compra, ed_p_ref, ed_p_venta)
                    st.success("¡Proyecto actualizado correctamente!")
                    st.rerun()
                if btn_del_proy:
                    eliminar_proyecto(id_proy_sel)
                    st.success("¡Proyecto eliminado correctamente!")
                    st.rerun()
                    
    with tab5:
        st.subheader("📑 ABM de Proveedores Registrados")
        with st.form("form_nuevo_proveedor", clear_on_submit=True):
            st.markdown('<p class="field-title">Nombre del Proveedor (ej. SBG)</p>', unsafe_allow_html=True)
            p_nombre = st.text_input("Nombre del Proveedor (ej. SBG)", label_visibility="collapsed")
            st.markdown('<p class="field-title">Rubro Principal</p>', unsafe_allow_html=True)
            p_rubro = st.selectbox("Rubro Principal", get_rubros(), label_visibility="collapsed")
            st.markdown('<p class="field-title">Datos de Contacto / Local</p>', unsafe_allow_html=True)
            p_contacto = st.text_input("Datos de Contacto / Local", label_visibility="collapsed")
            
            if st.form_submit_button("➕ Guardar Proveedor"):
                if p_nombre:
                    if agregar_proveedor(p_nombre, p_rubro, p_contacto):
                        st.success(f"Proveedor '{p_nombre}' guardado exitosamente.")
                        st.rerun()
                    else:
                        st.error("El proveedor ya existe en la base de datos.")
                else:
                    st.warning("Ingresá el nombre del proveedor.")
                    
        st.markdown("---")
        st.subheader("📂 Proveedores en Base de Datos (Modificar / Eliminar)")
        df_prov = get_proveedores_df()
        df_prov_display = df_prov.copy()
        df_prov_display.columns = ["ID", "Proveedor", "Rubro Principal", "Contacto"]
        st.dataframe(df_prov_display, use_container_width=True)
        
        if not df_prov.empty:
            st.markdown('<p class="field-title">Seleccionar ID de Proveedor a Modificar/Eliminar</p>', unsafe_allow_html=True)
            id_prov_sel = st.selectbox("Seleccionar ID de Proveedor a Modificar/Eliminar", df_prov["id"].tolist(), label_visibility="collapsed")
            reg_prov = df_prov[df_prov["id"] == id_prov_sel].iloc[0]
            
            with st.form("form_editar_proveedor"):
                st.markdown(f"**Editando Proveedor ID: {id_prov_sel}**")
                st.markdown('<p class="field-title">Nombre del Proveedor</p>', unsafe_allow_html=True)
                ed_prov_nombre = st.text_input("Nombre", value=reg_prov["nombre"], label_visibility="collapsed")
                st.markdown('<p class="field-title">Rubro Principal</p>', unsafe_allow_html=True)
                lista_rubros_disp = get_rubros()
                idx_rubro_prov = lista_rubros_disp.index(reg_prov["rubro_principal"]) if reg_prov["rubro_principal"] in lista_rubros_disp else 0
                ed_prov_rubro = st.selectbox("Rubro Principal", lista_rubros_disp, index=idx_rubro_prov, label_visibility="collapsed")
                st.markdown('<p class="field-title">Datos de Contacto / Local</p>', unsafe_allow_html=True)
                ed_prov_contacto = st.text_input("Contacto", value=str(reg_prov["contacto"]), label_visibility="collapsed")
                
                btn_act_prov = st.form_submit_button("🔄 Actualizar Proveedor")
                btn_del_prov = st.form_submit_button("🗑️ Eliminar Proveedor")
                
                if btn_act_prov:
                    actualizar_proveedor(id_prov_sel, ed_prov_nombre, ed_prov_rubro, ed_prov_contacto)
                    st.success("¡Proveedor actualizado correctamente!")
                    st.rerun()
                if btn_del_prov:
                    eliminar_proveedor(id_prov_sel)
                    st.success("¡Proveedor eliminado correctamente!")
                    st.rerun()
                    
    with tab6:
        st.subheader("🛠️ Administración de Categorías de Rubros")
        with st.form("form_nuevo_rubro", clear_on_submit=True):
            st.markdown('<p class="field-title">Nombre del Nuevo Rubro</p>', unsafe_allow_html=True)
            nuevo_cat = st.text_input("Nombre del Nuevo Rubro", label_visibility="collapsed")
            if st.form_submit_button("➕ Agregar Rubro") and nuevo_cat:
                if agregar_rubro(nuevo_cat):
                    st.success(f"Rubro '{nuevo_cat}' agregado con éxito.")
                    st.rerun()
                else:
                    st.error("El rubro ya existe en la base de datos.")
                    
        st.markdown("---")
        st.subheader("📂 Rubros Activos (Modificar / Eliminar)")
        df_rubros_db = get_rubros_df()
        df_rubros_display = df_rubros_db.copy()
        df_rubros_display.columns = ["ID", "Rubro de Obra"]
        st.dataframe(df_rubros_display, use_container_width=True)
        
        if not df_rubros_db.empty:
            st.markdown('<p class="field-title">Seleccionar ID de Rubro a Modificar/Eliminar</p>', unsafe_allow_html=True)
            id_rubro_sel = st.selectbox("Seleccionar ID de Rubro a Modificar/Eliminar", df_rubros_db["id"].tolist(), label_visibility="collapsed")
            reg_rubro = df_rubros_db[df_rubros_db["id"] == id_rubro_sel].iloc[0]
            
            with st.form("form_editar_rubro"):
                st.markdown(f"**Editando Rubro ID: {id_rubro_sel}**")
                st.markdown('<p class="field-title">Nombre del Rubro</p>', unsafe_allow_html=True)
                ed_rubro_nombre = st.text_input("Nombre del Rubro", value=reg_rubro["nombre"], label_visibility="collapsed")
                
                btn_act_rubro = st.form_submit_button("🔄 Actualizar Rubro")
                btn_del_rubro = st.form_submit_button("🗑️ Eliminar Rubro")
                
                if btn_act_rubro:
                    if actualizar_rubro(id_rubro_sel, ed_rubro_nombre):
                        st.success("¡Rubro actualizado correctamente!")
                        st.rerun()
                    else:
                        st.error("El nombre del rubro ya existe.")
                if btn_del_rubro:
                    eliminar_rubro(id_rubro_sel)
                    st.success("¡Rubro eliminado correctamente!")
                    st.rerun()
                    
    with tab7:
        st.subheader("💳 ABM de Medios de Pago y Tarjetas")
        with st.form("form_nuevo_mp", clear_on_submit=True):
            st.markdown('<p class="field-title">Nombre del Medio / Tarjeta (ej. Visa Galicia)</p>', unsafe_allow_html=True)
            mp_nombre = st.text_input("Nombre del Medio / Tarjeta (ej. Visa Galicia)", label_visibility="collapsed")
            st.markdown('<p class="field-title">Tipo</p>', unsafe_allow_html=True)
            mp_tipo = st.selectbox("Tipo", ["Tarjeta de Crédito", "Transferencia", "Efectivo", "Cheque", "Otro"], label_visibility="collapsed")
            st.markdown('<p class="field-title">Detalle / Cierre (ej. Cierre día 20)</p>', unsafe_allow_html=True)
            mp_detalle = st.text_input("Detalle / Cierre (ej. Cierre día 20)", label_visibility="collapsed")
            
            if st.form_submit_button("➕ Guardar Medio de Pago"):
                if mp_nombre:
                    if agregar_medio_pago(mp_nombre, mp_tipo, mp_detalle):
                        st.success(f"Medio de pago '{mp_nombre}' guardado con éxito.")
                        st.rerun()
                    else:
                        st.error("El medio de pago ya existe.")
                else:
                    st.warning("Ingresá el nombre.")
                    
        st.markdown("---")
        st.subheader("📂 Medios de Pago Registrados (Modificar / Eliminar)")
        df_mp_db = get_medios_pago_df()
        df_mp_display = df_mp_db.copy()
        df_mp_display.columns = ["ID", "Medio de Pago", "Tipo", "Detalle"]
        st.dataframe(df_mp_display, use_container_width=True)
        
        if not df_mp_db.empty:
            st.markdown('<p class="field-title">Seleccionar ID de Medio de Pago a Modificar/Eliminar</p>', unsafe_allow_html=True)
            id_mp_sel = st.selectbox("Seleccionar ID de Medio de Pago a Modificar/Eliminar", df_mp_db["id"].tolist(), label_visibility="collapsed")
            reg_mp = df_mp_db[df_mp_db["id"] == id_mp_sel].iloc[0]
            
            with st.form("form_editar_mp"):
                st.markdown(f"**Editando Medio de Pago ID: {id_mp_sel}**")
                st.markdown('<p class="field-title">Nombre del Medio / Tarjeta</p>', unsafe_allow_html=True)
                ed_mp_nombre = st.text_input("Nombre", value=reg_mp["nombre"], label_visibility="collapsed")
                st.markdown('<p class="field-title">Tipo</p>', unsafe_allow_html=True)
                tipos_disp = ["Tarjeta de Crédito", "Transferencia", "Efectivo", "Cheque", "Otro"]
                idx_tipo = tipos_disp.index(reg_mp["tipo"]) if reg_mp["tipo"] in tipos_disp else 0
                ed_mp_tipo = st.selectbox("Tipo", tipos_disp, index=idx_tipo, label_visibility="collapsed")
                st.markdown('<p class="field-title">Detalle / Cierre</p>', unsafe_allow_html=True)
                ed_mp_detalle = st.text_input("Detalle", value=str(reg_mp["detalle"]), label_visibility="collapsed")
                
                btn_act_mp = st.form_submit_button("🔄 Actualizar Medio de Pago")
                btn_del_mp = st.form_submit_button("🗑️ Eliminar Medio de Pago")
                
                if btn_act_mp:
                    actualizar_medio_pago(id_mp_sel, ed_mp_nombre, ed_mp_tipo, ed_mp_detalle)
                    st.success("¡Medio de pago actualizado correctamente!")
                    st.rerun()
                if btn_del_mp:
                    eliminar_medio_pago(id_mp_sel)
                    st.success("¡Medio de pago eliminado correctamente!")
                    st.rerun()
                    
    with tab8:
        st.subheader("📋 ABM y Carga de Presupuestos de Reforma")
        with st.form("form_pto_rubro", clear_on_submit=True):
            c_p1, c_p2, c_p3 = st.columns(3)
            with c_p1:
                st.markdown('<p class="field-title">📂 Rubro de Obra</p>', unsafe_allow_html=True)
                p_rubro = st.selectbox("Rubro Ppto", get_rubros(), label_visibility="collapsed")
            with c_p2:
                st.markdown('<p class="field-title">📑 Proveedor</p>', unsafe_allow_html=True)
                p_prov = st.selectbox("Proveedor Ppto", get_proveedores(), label_visibility="collapsed")
            with c_p3:
                st.markdown('<p class="field-title">🏠 Ambiente</p>', unsafe_allow_html=True)
                p_ambiente = st.selectbox("Ambiente Ppto", ["Cocina", "Baño 1", "Baño 2", "Toilette", "Living y Pasillos", "Balcón", "General"], label_visibility="collapsed")
                
            c_p4, c_p5, c_p6 = st.columns(3)
            with c_p4:
                st.markdown('<p class="field-title">💬 Concepto / Tarea</p>', unsafe_allow_html=True)
                p_concepto = st.text_input("Concepto Ppto", value="Ej: Provisión y colocación", label_visibility="collapsed")
            with c_p5:
                st.markdown('<p class="field-title">💱 Moneda</p>', unsafe_allow_html=True)
                p_moneda = st.selectbox("Moneda", ["ARS", "USD"], label_visibility="collapsed")
            with c_p6:
                st.markdown('<p class="field-title">💵 Monto Presupuestado</p>', unsafe_allow_html=True)
                p_monto = st.number_input("Monto Ppto", min_value=0, value=500000, step=10000, format="%d", label_visibility="collapsed")
                
            if st.form_submit_button("💾 Guardar Presupuesto"):
                if p_concepto:
                    guardar_presupuesto_rubro(proyecto_id_activo, p_rubro, p_ambiente, p_prov, p_concepto, p_moneda, p_monto)
                    st.success("¡Presupuesto guardado con éxito!")
                    st.rerun()
                else:
                    st.warning("Ingresá un concepto para el presupuesto.")
                    
        st.markdown("---")
        st.subheader("📂 Presupuestos Registrados (Modificar, Gestionar y Borrar)")
        df_ppto_db = get_presupuestos(proyecto_id_activo)
        
        if not df_ppto_db.empty:
            tc_ref_ppto = 1250
            df_pagos_ppto_ref = get_pagos(proyecto_id_activo)
            if not df_pagos_ppto_ref.empty and "tipo_cambio" in df_pagos_ppto_ref.columns:
                tc_prom_p = df_pagos_ppto_ref["tipo_cambio"].mean()
                if tc_prom_p > 0:
                    tc_ref_ppto = int(tc_prom_p)
                    
            tot_ppto_ars = 0
            tot_ppto_usd = 0
            for idx, r_row in df_ppto_db.iterrows():
                if r_row["moneda"] == "ARS":
                    tot_ppto_ars += r_row["monto_presupuestado"]
                    tot_ppto_usd += int(r_row["monto_presupuestado"] / tc_ref_ppto) if tc_ref_ppto > 0 else 0
                else:
                    tot_ppto_usd += r_row["monto_presupuestado"]
                    tot_ppto_ars += int(r_row["monto_presupuestado"] * tc_ref_ppto)
                    
            st.markdown(f"**TOTALES GENERALES PRESUPUESTO:** 💵 **${int(tot_ppto_ars):,} ARS** | 💲 **${int(tot_ppto_usd):,} USD**".replace(",", "."), unsafe_allow_html=True)
            
            df_ppto_viz = df_ppto_db.copy()
            df_ppto_viz.columns = ["ID", "Proj ID", "Rubro", "Ambiente", "Proveedor", "Concepto", "Moneda", "Monto"]
            st.dataframe(df_ppto_viz, use_container_width=True)
            
            st.markdown('<p class="field-title">Seleccioná el ID del presupuesto a modificar o eliminar</p>', unsafe_allow_html=True)
            id_ppto_gest = st.selectbox("Seleccioná el ID del presupuesto a modificar o eliminar", df_ppto_db["id"].tolist(), label_visibility="collapsed")
            reg_ppto = df_ppto_db[df_ppto_db["id"] == id_ppto_gest].iloc[0]
            
            with st.form("form_editar_presupuesto"):
                st.markdown(f"**Editando Presupuesto ID: {id_ppto_gest}**")
                st.markdown('<p class="field-title">📂 Rubro de Obra</p>', unsafe_allow_html=True)
                ed_pto_rubro = st.selectbox("Rubro", get_rubros(), index=get_rubros().index(reg_ppto["rubro"]) if reg_ppto["rubro"] in get_rubros() else 0, label_visibility="collapsed")
                st.markdown('<p class="field-title">🏠 Ambiente</p>', unsafe_allow_html=True)
                amb_lista = ["Cocina", "Baño 1", "Baño 2", "Toilette", "Living y Pasillos", "Balcón", "General"]
                ed_pto_amb = st.selectbox("Ambiente", amb_lista, index=amb_lista.index(reg_ppto["ambiente"]) if reg_ppto["ambiente"] in amb_lista else 0, label_visibility="collapsed")
                st.markdown('<p class="field-title">📑 Proveedor</p>', unsafe_allow_html=True)
                ed_pto_prov = st.selectbox("Proveedor", get_proveedores(), index=get_proveedores().index(reg_ppto["proveedor"]) if reg_ppto["proveedor"] in get_proveedores() else 0, label_visibility="collapsed")
                st.markdown('<p class="field-title">💬 Concepto / Tarea</p>', unsafe_allow_html=True)
                ed_pto_conc = st.text_input("Concepto", value=reg_ppto["concepto"], label_visibility="collapsed")
                st.markdown('<p class="field-title">💱 Moneda</p>', unsafe_allow_html=True)
                ed_pto_mon = st.selectbox("Moneda", ["ARS", "USD"], index=0 if reg_ppto["moneda"] == "ARS" else 1, label_visibility="collapsed")
                st.markdown('<p class="field-title">💵 Monto Presupuestado</p>', unsafe_allow_html=True)
                ed_pto_monto = st.number_input("Monto Presupuestado", value=int(reg_ppto["monto_presupuestado"]), step=10000, format="%d", label_visibility="collapsed")
                
                btn_act_pto = st.form_submit_button("🔄 Actualizar Presupuesto")
                btn_del_pto = st.form_submit_button("🗑️ Eliminar Presupuesto")
                
                if btn_act_pto:
                    actualizar_presupuesto(id_ppto_gest, ed_pto_rubro, ed_pto_amb, ed_pto_prov, ed_pto_conc, ed_pto_mon, ed_pto_monto)
                    st.success("¡Presupuesto actualizado correctamente!")
                    st.rerun()
                if btn_del_pto:
                    eliminar_presupuesto(id_ppto_gest)
                    st.success("¡Presupuesto eliminado correctamente!")
                    st.rerun()
        else:
            st.info("No hay presupuestos cargados.")
            
    with tab9:
        render_panel_financiero()
    with tab10:
        render_escenarios_venta()

else:
    # ==========================================
    # VISTA INVERSORA / CLIENTE
    # ==========================================
    with tab_cli_1:
        render_especificaciones_tab()
    with tab_cli_2:
        render_reportes_tab()
    with tab_cli_3:
        render_panel_financiero()
    with tab_cli_4:
        render_escenarios_venta()
