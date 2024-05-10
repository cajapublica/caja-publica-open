
import os
import streamlit as st
from utils import *

def main_entidades(tipo_contrato, year_slider):

    # Current radio in environment variable:
    os.environ['RADIO'] = "Por entidad estatal"

    # Input box for cedula
    nit = st.text_input("Ingrese un NIT", value="")
    nit = nit.replace(".", "").replace(",", "")
    nit = nit.replace("-", "")

    # Keep only first 9 digits
    nit = nit[:9]

    print("nit: ", nit)

    # If nit is empty, stop
    if nit == "":
        st.stop()

    query = f"""
    WITH personas_de_esta_entidad_v0 AS (

        SELECT *
        FROM personas_naturales
        WHERE nit_entidad = '{nit}'
    ),

    personas_de_esta_entidad AS (

        SELECT documento_persona AS id, nombre_persona AS nombre, SUM(valor_contrato_millones) AS suma_contratos_millones, COUNT(id_unico) AS total_numero_contratos
        FROM personas_de_esta_entidad_v0
        GROUP BY documento_persona, nombre_persona
        
    ),

    personas_con_mas_plata AS (
        
        SELECT 
            *,
        'naturales_mas_dinero' AS tipo
        FROM personas_de_esta_entidad
        ORDER BY suma_contratos_millones DESC
        LIMIT 10
        
        
            
    ),

    personas_con_mas_contratos AS (

        SELECT 
            *,
        'naturales_mas_contratos' AS tipo
        FROM personas_de_esta_entidad
        ORDER BY total_numero_contratos DESC
        LIMIT 10 
    ),

    juridicas_de_esta_entidad AS (

        SELECT nit_empresa AS id, nombre_empresa AS nombre, SUM(valor_contrato_millones) AS suma_contratos_millones, COUNT(id_unico) AS total_numero_contratos
        FROM personas_juridicas
        WHERE nit_entidad = '{nit}'
        GROUP BY nit_empresa, nombre_empresa
        
    ),


    juridicas_con_mas_plata AS (
        
        SELECT 
            *,
        'juridicas_mas_dinero' AS tipo
        FROM juridicas_de_esta_entidad
        ORDER BY suma_contratos_millones DESC
        LIMIT 10
        
            
    ),

    juridicas_con_mas_contratos AS (

        SELECT 
            *,
        'juridicas_mas_contratos' AS tipo
        FROM juridicas_de_esta_entidad
        ORDER BY total_numero_contratos DESC
        LIMIT 10 
    ),

    personas_con_varios_roles AS (

        SELECT 
            documento_persona AS id, 
            nombre_persona AS nombre, 
            COUNT(DISTINCT tipo_relacion) AS suma_contratos_millones, 
            -1 AS total_numero_contratos, 
            'personas_con_varios_roles' AS tipo
        FROM personas_de_esta_entidad_v0
        GROUP BY documento_persona, nombre_persona
        HAVING COUNT(DISTINCT tipo_relacion) > 1

    )

    select * from personas_con_mas_plata  union all 
    select * from personas_con_mas_contratos union all
    select * from juridicas_con_mas_plata union all
    select * from juridicas_con_mas_contratos union all
    select * from personas_con_varios_roles

    """

    with st.spinner('Buscando...'):
        df = query_postgres(query)

    df["suma_contratos_millones"] = df["suma_contratos_millones"].astype(float)
    df["total_numero_contratos"] = df["total_numero_contratos"].astype(int)

    # st.dataframe(df)

    # st.dataframe(df[df['tipo'] == 'naturales_mas_dinero'])

    st.title("Análisis de personas")

    # horizontal bar chart with plotly express
    import plotly.express as px


    # horizontal bar chart with st.
    st.header("Personas que más plata han recibido")
    
    naturales_mas_dinero = df[df['tipo'] == 'naturales_mas_dinero'].sort_values(by='suma_contratos_millones', ascending=True)
    fig = px.bar(naturales_mas_dinero, x='suma_contratos_millones', y='nombre')
    st.plotly_chart(fig, use_container_width=True)

    # Opcion para ver datos en tabla
    expander = st.expander("Ver datos crudos en una tabla")
    expander.dataframe(naturales_mas_dinero.drop(columns=['tipo']))



    # horizontal bar chart with st.
    st.header("Personas con más contratos")
    naturales_mas_contratos = df[df['tipo'] == 'naturales_mas_contratos'].sort_values(by='total_numero_contratos', ascending=True)
    fig = px.bar(naturales_mas_contratos, x='total_numero_contratos', y='nombre')
    # order by total_numero_contratos DESC

    st.plotly_chart(fig, use_container_width=True)

    # Opcion para ver datos en tabla
    expander = st.expander("Ver datos crudos en una tabla")
    expander.dataframe(naturales_mas_contratos.drop(columns=['tipo']))


    st.title("Análisis de empresas")

    # horizontal bar chart with st.
    st.header("Empresas que más plata han recibido")
    juridicas_mas_dinero = df[df['tipo'] == 'juridicas_mas_dinero'].sort_values(by='suma_contratos_millones', ascending=True)
    fig = px.bar(juridicas_mas_dinero, x='suma_contratos_millones', y='nombre')
    st.plotly_chart(fig, use_container_width=True)

    # Opcion para ver datos en tabla
    expander = st.expander("Ver datos crudos en una tabla")
    expander.dataframe(juridicas_mas_dinero.drop(columns=['tipo']))

    # horizontal bar chart with st.
    st.header("Empresas con más contratos")
    juridicas_mas_contratos = df[df['tipo'] == 'juridicas_mas_contratos'].sort_values(by='total_numero_contratos', ascending=True)
    fig = px.bar(juridicas_mas_contratos, x='total_numero_contratos', y='nombre')
    st.plotly_chart(fig, use_container_width=True)

    # Opcion para ver datos en tabla
    expander = st.expander("Ver datos crudos en una tabla")
    expander.dataframe(juridicas_mas_contratos.drop(columns=['tipo']))

    st.title("Personas con varios roles")

    personas_con_varios_roles = df[df['tipo'] == 'personas_con_varios_roles']
    st.dataframe(personas_con_varios_roles)





