import streamlit as st
import requests
import gzip
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS
st.set_page_config(page_title="Guía de Canales de Televisión", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    
    .main { background-color: #151515; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #262626; color: white; border: 1px solid #404040; }
    .stButton>button:hover { background-color: #00d2ff; color: white; border-color: #00d2ff; }
    
    .time-badge { color: #a855f7; font-weight: bold; font-size: 16px; }
    .prog-title { color: #38bdf8; font-weight: bold; font-size: 18px; }
    .live-indicator { color: #22c55e; font-weight: bold; font-size: 13px; }
    
    .live-program-box { 
        border: 2px solid #00d2ff; 
        box-shadow: 0px 0px 12px #00d2ff; 
        border-radius: 8px; 
        padding: 10px; 
        background-color: #1e293b; 
    }
    .normal-program-box {
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

LOGO_DEFAULT = "https://cdn-icons-png.flaticon.com/512/716/716429.png"
POSTER_DEFAULT = "https://images.unsplash.com/photo-1593789198777-f29bc259780e?q=80&w=300&auto=format&fit=crop"

# Detectar la zona horaria del usuario de forma predeterminada
tz_local = pytz.timezone('America/Caracas')
now_local = datetime.now(tz_local)

# BASE DE DATOS GLOBAL DE FUENTES EPG
EPG_SOURCES = {
    "Albania": "https://iptv-epg.org/files/epg-al.xml.gz",
    "Argentina": "https://iptv-epg.org/files/epg-ar.xml.gz",
    "Armenia": "https://iptv-epg.org/files/epg-am.xml.gz",
    "Australia": "https://iptv-epg.org/files/epg-au.xml.gz",
    "Austria": "https://iptv-epg.org/files/epg-at.xml.gz",
    "Bahamas": "https://iptv-epg.org/files/epg-bs.xml.gz",
    "Belarus": "https://iptv-epg.org/files/epg-by.xml.gz",
    "Belgium": "https://iptv-epg.org/files/epg-be.xml.gz",
    "Bolivia": "https://iptv-epg.org/files/epg-bo.xml.gz",
    "Bosnia & Herzegovina": "https://iptv-epg.org/files/epg-ba.xml.gz",
    "Brazil": "https://iptv-epg.org/files/epg-br.xml.gz",
    "Bulgaria": "https://iptv-epg.org/files/epg-bg.xml.gz",
    "Canada": "https://iptv-epg.org/files/epg-ca.xml.gz",
    "Chile": "https://iptv-epg.org/files/epg-cl.xml.gz",
    "Colombia": "https://iptv-epg.org/files/epg-co.xml.gz",
    "Costa Rica": "https://iptv-epg.org/files/epg-cr.xml.gz",
    "Croatia": "https://iptv-epg.org/files/epg-hr.xml.gz",
    "Curacao": "https://iptv-epg.org/files/epg-cw.xml.gz",
    "Czech Republic": "https://iptv-epg.org/files/epg-cz.xml.gz",
    "Denmark": "https://iptv-epg.org/files/epg-dk.xml.gz",
    "Dominican Republic": "https://iptv-epg.org/files/epg-do.xml.gz",
    "Egypt": "https://iptv-epg.org/files/epg-eg.xml.gz",
    "El Salvador": "https://iptv-epg.org/files/epg-sv.xml.gz",
    "Finland": "https://iptv-epg.org/files/epg-fi.xml.gz",
    "France": "https://iptv-epg.org/files/epg-fr.xml.gz",
    "Georgia": "https://iptv-epg.org/files/epg-ge.xml.gz",
    "Germany": "https://iptv-epg.org/files/epg-de.xml.gz",
    "Ghana": "https://iptv-epg.org/files/epg-gh.xml.gz",
    "Greece": "https://iptv-epg.org/files/epg-gr.xml.gz",
    "Guatemala": "https://iptv-epg.org/files/epg-gt.xml.gz",
    "Honduras": "https://iptv-epg.org/files/epg-hn.xml.gz",
    "Hong Kong": "https://iptv-epg.org/files/epg-hk.xml.gz",
    "Hungary": "https://iptv-epg.org/files/epg-hu.xml.gz",
    "Iceland": "https://iptv-epg.org/files/epg-is.xml.gz",
    "India": "https://iptv-epg.org/files/epg-in.xml.gz",
    "Indonesia": "https://iptv-epg.org/files/epg-id.xml.gz",
    "Israel": "https://iptv-epg.org/files/epg-il.xml.gz",
    "Italy": "https://iptv-epg.org/files/epg-it.xml.gz",
    "Jamaica": "https://iptv-epg.org/files/epg-jm.xml.gz",
    "Lebanon": "https://iptv-epg.org/files/epg-lb.xml.gz",
    "Lithuania": "https://iptv-epg.org/files/epg-lt.xml.gz",
    "Luxembourg": "https://iptv-epg.org/files/epg-lu.xml.gz",
    "Macedonia": "https://iptv-epg.org/files/epg-mk.xml.gz",
    "Malaysia": "https://iptv-epg.org/files/epg-my.xml.gz",
    "Malta": "https://iptv-epg.org/files/epg-mt.xml.gz",
    "Mexico": "https://iptv-epg.org/files/epg-mx.xml.gz",
    "Montenegro": "https://iptv-epg.org/files/epg-me.xml.gz",
    "Netherlands": "https://iptv-epg.org/files/epg-nl.xml.gz",
    "New Zealand": "https://iptv-epg.org/files/epg-nz.xml.gz",
    "Nicaragua": "https://iptv-epg.org/files/epg-ni.xml.gz",
    "Nigeria": "https://iptv-epg.org/files/epg-ng.xml.gz",
    "Norway": "https://iptv-epg.org/files/epg-no.xml.gz",
    "Panama": "https://iptv-epg.org/files/epg-pa.xml.gz",
    "Paraguay": "https://iptv-epg.org/files/epg-py.xml.gz",
    "Peru": "https://iptv-epg.org/files/epg-pe.xml.gz",
    "Philippines": "https://iptv-epg.org/files/epg-ph.xml.gz",
    "Poland": "https://iptv-epg.org/files/epg-pl.xml.gz",
    "Portugal": "https://iptv-epg.org/files/epg-pt.xml.gz",
    "Romania": "https://iptv-epg.org/files/epg-ro.xml.gz",
    "Russia": "https://iptv-epg.org/files/epg-ru.xml.gz",
    "Serbia": "https://iptv-epg.org/files/epg-rs.xml.gz",
    "Singapore": "https://iptv-epg.org/files/epg-sg.xml.gz",
    "Slovenia": "https://iptv-epg.org/files/epg-si.xml.gz",
    "South Africa": "https://iptv-epg.org/files/epg-za.xml.gz",
    "South Korea": "https://iptv-epg.org/files/epg-kr.xml.gz",
    "Spain": "https://iptv-epg.org/files/epg-es.xml.gz",
    "Sweden": "https://iptv-epg.org/files/epg-se.xml.gz",
    "Switzerland": "https://iptv-epg.org/files/epg-ch.xml.gz",
    "Taiwan": "https://iptv-epg.org/files/epg-tw.xml.gz",
    "Thailand": "https://iptv-epg.org/files/epg-th.xml.gz",
    "Trinidad & Tobago": "https://iptv-epg.org/files/epg-tt.xml.gz",
    "Turkey": "https://iptv-epg.org/files/epg-tr.xml.gz",
    "Uganda": "https://iptv-epg.org/files/epg-ug.xml.gz",
    "Ukraine": "https://iptv-epg.org/files/epg-ua.xml.gz",
    "United Arab Emirates": "https://iptv-epg.org/files/epg-ae.xml.gz",
    "United Kingdom": "https://iptv-epg.org/files/epg-gb.xml.gz",
    "United States": "https://iptv-epg.org/files/epg-us.xml.gz",
    "Uruguay": "https://iptv-epg.org/files/epg-uy.xml.gz",
    "Venezuela": "https://iptv-epg.org/files/epg-ve.xml.gz",
    "Zimbabwe": "https://iptv-epg.org/files/epg-zw.xml.gz"
}

# Inicializar estados de la sesión
if 'selected_channel' not in st.session_state:
    st.session_state['selected_channel'] = None
if 'dias_offset' not in st.session_state:
    st.session_state['dias_offset'] = 0

# Encabezado principal
col_header_left, col_header_right = st.columns([3, 1])
with col_header_left:
    st.title("Guía de Canales de Televisión")
with col_header_right:
    pais_sel = st.selectbox("Cambiar Región:", list(EPG_SOURCES.keys()), index=list(EPG_SOURCES.keys()).index("Venezuela"))

def parsear_fecha_xml_a_local(fecha_str):
    try:
        limpia = fecha_str.split()[0][:14]
        utc_dt = datetime.strptime(limpia, "%Y%m%d%H%M%S").replace(tzinfo=pytz.utc)
        return utc_dt.astimezone(tz_local)
    except:
        return None

@st.cache_data(ttl=900)
def procesar_datos_epg(url):
    try:
        response = requests.get(url, timeout=20)
        xml_data = gzip.decompress(response.content)
        root = ET.fromstring(xml_data)
        
        canales = {}
        for channel in root.findall('channel'):
            c_id = channel.get('id')
            name = channel.find('display-name').text if channel.find('display-name') is not None else c_id
            icon = channel.find('icon')
            logo = icon.get('src') if icon is not None else LOGO_DEFAULT
            if not logo or logo.strip() == "": logo = LOGO_DEFAULT
            canales[c_id] = {"nombre": name, "logo": logo}
            
        programas = []
        for prog in root.findall('programme'):
            c_id = prog.get('channel')
            if c_id not in canales: continue
            
            dt_start = parsear_fecha_xml_a_local(prog.get('start'))
            dt_stop = parsear_fecha_xml_a_local(prog.get('stop'))
            if not dt_start or not dt_stop: continue
            
            title = prog.find('title').text if prog.find('title') is not None else "Sin Título"
            desc = prog.find('desc').text if prog.find('desc') is not None else "Sin descripción disponible."
            
            icon_prog = prog.find('icon')
            img_prog = icon_prog.get('src') if icon_prog is not None else POSTER_DEFAULT
            if not img_prog or img_prog.strip() == "": img_prog = POSTER_DEFAULT
            
            programas.append({
                "channel_id": c_id,
                "canal_nombre": canales[c_id]["nombre"],
                "canal_logo": canales[c_id]["logo"],
                "start": dt_start,
                "stop": dt_stop,
                "titulo": title,
                "descripcion": desc,
                "imagen": img_prog
            })
        return canales, programas
    except Exception as e:
        st.error(f"Error cargando guía: {e}")
        return {}, []

canales_dict, lista_programas = procesar_datos_epg(EPG_SOURCES[pais_sel])

# =========================================================================
# VISTA 1: HOME - PRESENTÁNDOSE EN ESTE MOMENTO
# =========================================================================
if st.session_state['selected_channel'] is None:
    st.markdown("## Presentándose en este momento")
    st.write(f"Hora actual en tu región: **{now_local.strftime('%I:%M %p')}**")
    
    query = st.text_input("Buscar películas, series o canales favoritos:")

    on_air = [p for p in lista_programas if p['start'] <= now_local <= p['stop']]
    
    if query:
        on_air = [p for p in on_air if query.lower() in p['canal_nombre'].lower() or query.lower() in p['titulo'].lower()]

    if on_air:
        for p in on_air[:20]: 
            with st.container():
                c_img, c_title, c_logo, c_time = st.columns([1.5, 3, 2, 1.5])
                with c_img:
                    st.image(p['imagen'], use_container_width=True)
                with c_title:
                    st.markdown(f"<p class='prog-title'>{p['titulo']}</p>", unsafe_allow_html=True)
                    min_left = int((p['stop'] - now_local).total_seconds() / 60)
                    st.markdown(f"<p class='live-indicator'>EN VIVO (Termina en {min_left} min)</p>", unsafe_allow_html=True)
                    st.write(p['descripcion'])
                with c_logo:
                    st.image(p['canal_logo'], width=75)
                    if st.button(f"Ver Guía de\n{p['canal_nombre']}", key=f"btn_{p['channel_id']}_{p['start'].strftime('%M%S')}"):
                        st.session_state['selected_channel'] = p['channel_id']
                        st.session_state['dias_offset'] = 0
                        st.rerun()
                with c_time:
                    slot = f"{p['start'].strftime('%I:%M %p')} - {p['stop'].strftime('%I:%M %p')}"
                    st.markdown(f"<p class='time-badge'>{slot}</p>", unsafe_allow_html=True)
                st.markdown("---")
    else:
        st.warning("No se encontraron canales transmitiendo datos en este huso horario.")

# =========================================================================
# VISTA 2: PARRILLA DEL CANAL SELECCIONADO
# =========================================================================
else:
    ch_id = st.session_state['selected_channel']
    canal_info = canales_dict.get(ch_id, {"nombre": "Canal Desconocido", "logo": LOGO_DEFAULT})
    
    if st.button("Volver a la cartelera general"):
        st.session_state['selected_channel'] = None
        st.rerun()
        
    st.markdown(f"## Programación completa de: {canal_info['nombre']}")
    
    st.image(canal_info['logo'], width=140)
    
    col_ant, col_hoy, col_sig = st.columns([1, 1, 1])
    with col_ant:
        if st.button("Día Anterior"):
            st.session_state['dias_offset'] -= 1
            st.rerun()
    with col_hoy:
        if st.button("Hoy"):
            st.session_state['dias_offset'] = 0
            st.rerun()
    with col_sig:
        if st.button("Mañana"):
            st.session_state['dias_offset'] += 1
            st.rerun()

    target_date = now_local.date() + timedelta(days=st.session_state['dias_offset'])
    if st.session_state['dias_offset'] == 0:
        texto_fecha = "Hoy"
    elif st.session_state['dias_offset'] == 1:
        texto_fecha = "Mañana"
    elif st.session_state['dias_offset'] == -1:
        texto_fecha = "Ayer"
    else:
        texto_fecha = target_date.strftime('%A %d de %B')

    st.markdown(f"### Horarios para el día: **{texto_fecha}**")
    
    prog_canal = [p for p in lista_programas if p['channel_id'] == ch_id and p['start'].date() == target_date]
    prog_canal = sorted(prog_canal, key=lambda x: x['start'])
    
    if prog_canal:
        st.markdown("<div style='background-color:#0284c7; padding:10px; border-radius:4px; text-align:center; font-weight:bold; margin-bottom:15px;'>Horarios de Programación Oficial</div>", unsafe_allow_html=True)
        
        for p in prog_canal:
            es_en_vivo = (p['start'] <= now_local <= p['stop'])
            clase_caja = "live-program-box" if es_en_vivo else "normal-program-box"
            
            st.markdown(f"<div class='{clase_caja}'>", unsafe_allow_html=True)
            
            c_h_ini, c_h_fin, c_detalles = st.columns([1, 1, 6])
            with c_h_ini:
                st.markdown(f"**{p['start'].strftime('%I:%M %p')}**")
            with c_h_fin:
                st.markdown(f"<span style='color:#9ca3af;'>{p['stop'].strftime('%I:%M %p')}</span>", unsafe_allow_html=True)
            with c_detalles:
                col_sub_img, col_sub_txt = st.columns([1, 5])
                with col_sub_img:
                    st.image(p['imagen'], use_container_width=True)
                with col_sub_txt:
                    vivo_tag = " <span style='color:#00d2ff; font-size:12px; font-weight:bold;'>[TRANSMITIENDO AHORA]</span>" if es_en_vivo else ""
                    st.markdown(f"<span class='prog-title'>{p['titulo']}</span>{vivo_tag}", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#e5e7eb; font-size:13px; margin-top:2px;'>{p['descripcion']}</p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:8px 0; border-color:#262626;'>", unsafe_allow_html=True)
    else:
        st.info("No hay datos cargados para este canal en la fecha seleccionada.")
