import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000"

st.title("📈 StocksApp - Gestión de Acciones")

st.subheader("📊 Acciones Recomendadas")
recommended_response = requests.get(f"{API_URL}/acciones-recomendadas")
if recommended_response.status_code == 200:
    try:
        st.table(recommended_response.json())
    except requests.exceptions.JSONDecodeError:
        st.error("Error al decodificar la respuesta de las acciones recomendadas.")
else:
    st.error("Error al obtener los datos de las acciones recomendadas.")

st.subheader("🛒 Comprar Acción")
buy_symbol = st.text_input("Símbolo de la acción", "")
buy_quantity = st.number_input("Cantidad", min_value=1, step=1, value=1)
if st.button("Comprar"):
    buy_payload = {"symbol": buy_symbol, "quantity": buy_quantity}
    buy_response = requests.post(f"{API_URL}/compras", json=buy_payload)
    if buy_response.status_code == 201:
        st.success("Compra realizada con éxito")
    else:
        try:
            st.error(buy_response.json().get("error", "Error en la compra"))
        except requests.exceptions.JSONDecodeError:
            st.error("Error en la compra")

st.subheader("💰 Vender Acción")
sell_symbol = st.text_input("Símbolo de la acción a vender", "")
sell_quantity = st.number_input("Cantidad a vender", min_value=1, step=1, value=1)
if st.button("Vender"):
    sell_payload = {"symbol": sell_symbol, "quantity": sell_quantity}
    sell_response = requests.post(f"{API_URL}/ventas", json=sell_payload)
    if sell_response.status_code == 200:
        st.success("Venta realizada con éxito")
    else:
        try:
            st.error(sell_response.json().get("error", "Error en la venta"))
        except requests.exceptions.JSONDecodeError:
            st.error("Error en la venta")

st.subheader("📜 Mis Compras")
compras_response = requests.get(f"{API_URL}/compras")
if compras_response.status_code == 200:
    try:
        st.table(compras_response.json())
    except requests.exceptions.JSONDecodeError:
        st.error("Error al decodificar la respuesta de las compras.")
else:
    st.error("Error al obtener los datos de compras.")

st.subheader("📈 Acciones a Comprar")
acciones_comprar_response = requests.get(f"{API_URL}/acciones-comprar")
if acciones_comprar_response.status_code == 200:
    try:
        st.table(acciones_comprar_response.json())
    except requests.exceptions.JSONDecodeError:
        st.error("Error al decodificar la respuesta de las acciones a comprar.")
else:
    st.error("Error al obtener los datos de las acciones a comprar.")

st.caption("Desarrollado con Streamlit y Flask")
