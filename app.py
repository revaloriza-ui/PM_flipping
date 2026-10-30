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
