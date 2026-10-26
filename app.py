from datetime import datetime
import io
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

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

# --- CONEXIÓN DIRECTA Y SEGURA A SUPABASE ---
def init_db():
    return st.secrets["postgres"]["url"]

init_db()

# --- FUNCIONES DE BASE DE DATOS ---
def get_proyectos():
    conn = sqlite3.connect("flipping_multiproyecto.db")
    df = pd.read_sql("SELECT * FROM proyectos", conn)
    conn.close()
    return df

def get_proveedores():
    conn = sqlite3.connect("flipping_multiproyecto.db")
    df = pd.read_sql("SELECT * FROM proveedores", conn)
    conn.close()
    return df["nombre"].tolist()

def get_proveedores_df():
    conn = sqlite3.connect("flipping_multiproyecto.db")
    df = pd.read_sql("SELECT * FROM proveedores", conn)
    conn.close()
    return df

def agregar_proveedor(nombre, rubro, contacto):
    conn = sqlite3.connect("flipping_multiproyecto.db")
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
    conn = sqlite3.connect("flipping_multiproyecto.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE proveedores SET nombre = ?, rubro_principal = ?, contacto = ? WHERE id = ?
    """, (nombre, rubro, contacto, prov_id))
    conn.commit()
    conn.close()

def eliminar_proveedor(prov_id):
    conn = sqlite3.connect("flipping_multiproyecto.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proveedores WHERE id = ?", (prov_id,))
    conn.commit()
    conn.close()

def get_rubros():
    conn = sqlite3.connect("flipping_multiproyecto.db")
    df = pd.read_sql("SELECT * FROM rubros", conn)
    conn.close()
    return df["nombre"].tolist()

def get_rubros_df():
    conn = sqlite3.connect("flipping_multiproyecto.db")
    df = pd.read_sql("SELECT * FROM rubros", conn)
    conn.close()
    return df

def agregar_rubro(nuevo_rubro):
    conn = sqlite3.connect("flipping_multiproyecto.db")
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
    conn = sqlite3.connect("flipping_multiproyecto.db")
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
    conn = sqlite3.connect("flipping_multiproyecto.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rubros WHERE id = ?", (rubro_id,))
    conn.commit()
    conn.close()

def get_medios_pago():
    conn = sqlite3.connect("flipping_multiproyecto.db")
    df = pd.read_sql("SELECT * FROM medios_pago", conn)
    conn.close()
    return df["nombre"].tolist()

def get_medios_pago_df():
    conn = sqlite3.connect("flipping_multiproyecto.db")
    df = pd.read_sql("SELECT * FROM medios_pago", conn)
    conn.close()
    return df

def agregar_medio_pago(nombre, tipo, detalle):
    conn = sqlite3.connect("flipping_multiproyecto.db")
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
    conn = sqlite3.connect("flipping_multiproyecto.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE medios_pago SET nombre = ?, tipo = ?, detalle = ? WHERE id = ?
    """, (nombre, tipo, detalle, mp_id))
    conn.commit()
    conn.close()

def eliminar_medio_pago(mp_id):
    conn = sqlite3.connect("flipping_multiproyecto.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medios_pago WHERE id = ?", (mp_id,))
    conn.commit()
    conn.close()

def get_pagos(proyecto_id):
    conn = sqlite3.connect("flipping_multiproyecto.db")
    df = pd.read_sql("SELECT * FROM pagos WHERE proyecto_id = ?", conn, params=(proyecto_id,))
    conn.close()
    return df

def agregar_pago(proyecto_id, presupuesto_id, fecha, comprobante, tipo_gasto, medio_pago, cuotas, rubro, ambiente, proveedor, concepto, monto_ars, tipo_cambio):
    monto_usd = int(monto_ars / tipo_cambio) if tipo_cambio > 0 else 0
    conn = sqlite3.connect("flipping_multiproyecto.db")
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
    conn = sqlite3.connect("flipping_multiproyecto.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM especificaciones WHERE pago_id = ?", (pago_id,))
    cursor.execute("DELETE FROM pagos WHERE id = ?", (pago_id,))
    conn.commit()
    conn.close()

def actualizar_pago_completo(pago_id, presupuesto_id, fecha, comprobante, tipo_gasto, medio_pago, cuotas, rubro, ambiente, proveedor, concepto, monto_ars, tipo_cambio):
    monto_usd = int(monto_ars / tipo_cambio) if tipo_cambio > 0 else 0
    conn = sqlite3.connect("flipping_multiproyecto.db")
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

def get_presupuestos(proyecto_id):
    conn = sqlite3.connect("flipping_multiproyecto.db")
    df = pd.read_sql("SELECT * FROM presupuestos_rubro WHERE proyecto_id = ?", conn, params=(proyecto_id,))
    conn.close()
    return df

def guardar_presupuesto_rubro(proyecto_id, rubro, ambiente, proveedor, concepto, moneda, monto_presupuestado):
    conn = sqlite3.connect("flipping_multiproyecto.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO presupuestos_rubro (proyecto_id, rubro, ambiente, proveedor, concepto, moneda, monto_presupuestado) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (proyecto_id, rubro, ambiente, proveedor, concepto, moneda, int(monto_presupuestado)))
    conn.commit()
    conn.close()

def actualizar_presupuesto(ppto_id, rubro, ambiente, proveedor, concepto, moneda, monto_presupuestado):
    conn = sqlite3.connect("flipping_multiproyecto.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE presupuestos_rubro SET rubro = ?, ambiente = ?, proveedor = ?, concepto = ?, moneda = ?, monto_presupuestado = ? 
        WHERE id = ?
    """, (rubro, ambiente, proveedor, concepto, moneda, int(monto_presupuestado), ppto_id))
    conn.commit()
    conn.close()

def eliminar_presupuesto(ppto_id):
    conn = sqlite3.connect("flipping_multiproyecto.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM presupuestos_rubro WHERE id = ?", (ppto_id,))
    conn.commit()
    conn.close()

def get_especificaciones(proyecto_id):
    conn = sqlite3.connect("flipping_multiproyecto.db")
    df = pd.read_sql("SELECT * FROM especificaciones WHERE proyecto_id = ?", conn, params=(proyecto_id,))
    conn.close()
    return df

def actualizar_detalle_especificacion(esp_id, nuevos_detalles):
    conn = sqlite3.connect("flipping_multiproyecto.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE especificaciones SET detalles_tecnicos = ? WHERE id = ?
    """, (nuevos_detalles, esp_id))
    conn.commit()
    conn.close()

# --- BARRA LATERAL: SELECCIÓN DE PROYECTO Y ACCESO (DEFINIDA PRIMERO) ---
st.sidebar.header("🏢 Selector de Proyecto (ID)")
df_proyectos = get_proyectos()

if not df_proyectos.empty:
    proyectos_dict = {f"ID {row['id']}: {row['nombre']} (Cliente: {row['cliente']})": row["id"] for idx, row in df_proyectos.iterrows()}
    proyecto_sel_str = st.sidebar.selectbox("Seleccionar Proyecto Activo", list(proyectos_dict.keys()))
    proyecto_id_activo = proyectos_dict[proyecto_sel_str]
    proyecto_info = df_proyectos[df_proyectos["id"] == proyecto_id_activo].iloc[0]
else:
    proyecto_id_activo = 1
    proyecto_info = {"nombre": "Sin Proyecto", "cliente": "N/D", "superficie_total": 0, "precio_compra": 0, "presupuesto_reforma": 0, "precio_objetivo": 0}

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

# --- FUNCIÓN DE RESPALDO AUTOMÁTICO EN GOOGLE DRIVE ---
def hacer_backup_drive():
    try:
        gdrive_secrets = st.secrets["google_drive"]
        formatted_key = gdrive_secrets["private_key"].replace("\\n", "\n")
        
        credentials_info = {
            "type": "service_account",
            "project_id": "pm-flipping-backup",
            "private_key_id": "632234b40217f46df7adcdd014ef65b636ab09ad",
            "private_key": formatted_key,
            "client_email": gdrive_secrets["client_email"],
            "client_id": "103287396645637093815",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{gdrive_secrets['client_email'].replace('@', '%40')}",
            "universe_domain": "googleapis.com"
        }
        
        creds = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        service = build('drive', 'v3', credentials=creds)
        
        df_pagos_bk = get_pagos(proyecto_id_activo)
        df_proyectos_bk = get_proyectos()
        
        contenido_csv = "=== PROYECTOS ===\n"
        contenido_csv += df_proyectos_bk.to_csv(index=False)
        contenido_csv += "\n=== PAGOS DEL PROYECTO ===\n"
        contenido_csv += df_pagos_bk.to_csv(index=False)
        
        file_metadata = {
            'name': f'backup_pm_flipping_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            'parents': [gdrive_secrets["folder_id"]]
        }
        
        media = MediaIoBaseUpload(
            io.BytesIO(contenido_csv.encode('utf-8')),
            mimetype='text/csv',
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return True
    except Exception as e:
        st.error(f"Error al conectar con Google Drive: {e}")
        return False

# Botón de Respaldo en Google Drive en la Barra Lateral
st.sidebar.markdown("---")
st.sidebar.header("💾 Respaldo en la Nube")
if st.sidebar.button("Hacer Backup en Google Drive"):
    if hacer_backup_drive():
        st.sidebar.success("¡Respaldo subido a Google Drive con éxito!")

# --- INTERFAZ PRINCIPAL ---
st.title(f"🏗️ Panel Gerencial: {proyecto_info['nombre']}")
st.caption(f"Cliente / Inversor: {proyecto_info['cliente']} | Superficie: {sup_total} m²")

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
