import streamlit as st
import requests

# URL de la API Flask (ajústala según tu configuración)
API_URL = "http://127.0.0.1:5000"

st.title("📈 StocksApp - Gestión de Acciones")

# Obtener y mostrar las acciones recomendadas
st.subheader("📊 Acciones Recomendadas")
recommended_response = requests.get(f"{API_URL}/acciones-recomendadas")
if recommended_response.status_code == 200:
    try:
        recommended_data = recommended_response.json()
        st.table(recommended_data)
    except requests.exceptions.JSONDecodeError:
        st.error("Error al decodificar la respuesta de las acciones recomendadas.")
else:
    st.error("Error al obtener los datos de las acciones recomendadas.")

# Formulario para comprar acciones
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
            error_message = buy_response.json().get("error", "Error en la compra")
        except requests.exceptions.JSONDecodeError:
            error_message = "Error en la compra"
        st.error(error_message)

# Formulario para vender acciones
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
            error_message = sell_response.json().get("error", "Error en la venta")
        except requests.exceptions.JSONDecodeError:
            error_message = "Error en la venta"
        st.error(error_message)

# Obtener y mostrar las compras
st.subheader("📜 Mis Compras")
compras_response = requests.get(f"{API_URL}/compras")
if compras_response.status_code == 200:
    try:
        compras_data = compras_response.json()
        st.table(compras_data)
    except requests.exceptions.JSONDecodeError:
        st.error("Error al decodificar la respuesta de las compras.")
else:
    st.error("Error al obtener los datos de compras.")

st.caption("Desarrollado con Streamlit y Flask")
