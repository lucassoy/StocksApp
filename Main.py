import streamlit as st
import pandas as pd
from openpyxl import Workbook, load_workbook

# Cargar datos desde el Excel generado previamente
df = pd.read_excel("acciones.xlsx")

# Asegurar que la columna 'Symbol' existe y limpiar espacios
df["Symbol"] = df["Symbol"].astype(str).str.strip()

# Verificar si el archivo de recomendaciones existe y cargarlo
try:
    df_recomendadas = pd.read_excel("recomendaciones.xlsx")
except FileNotFoundError:
    st.error("El archivo 'recomendaciones.xlsx' no se encontró. Asegúrate de que se haya generado correctamente.")
    df_recomendadas = pd.DataFrame()

# Inicializar o cargar el archivo de compras
try:
    df_compras = pd.read_excel("compras.xlsx")
except FileNotFoundError:
    df_compras = pd.DataFrame(columns=["Symbol", "Name", "Price", "Quantity", "Total Investment", "Portfolio Percentage"])

# UI con Streamlit
st.title("📊 Análisis de Acciones")

# Sección para agregar nuevas compras
st.subheader("➕ Agregar nueva compra")
symbol = st.text_input("Símbolo de la acción", key="symbol_compra")
quantity = st.number_input("Cantidad de acciones", min_value=1, step=1, key="quantity_compra")

if st.button("Agregar compra"):
    if symbol and quantity > 0:
        # Buscar los datos de la acción en el archivo de acciones
        accion = df[df["Symbol"] == symbol]
        if not accion.empty:
            name = accion.iloc[0]["Name"]
            price = accion.iloc[0]["Price"]
            total_investment = price * quantity
            if symbol in df_compras["Symbol"].values:
                df_compras.loc[df_compras["Symbol"] == symbol, "Quantity"] += quantity
                df_compras.loc[df_compras["Symbol"] == symbol, "Total Investment"] += total_investment
            else:
                new_row = pd.DataFrame({
                    "Symbol": [symbol],
                    "Name": [name],
                    "Price": [price],
                    "Quantity": [quantity],
                    "Total Investment": [total_investment],
                    "Portfolio Percentage": [0]  # Se calculará más adelante
                })
                df_compras = pd.concat([df_compras, new_row], ignore_index=True)
            df_compras.to_excel("compras.xlsx", index=False)
            st.success(f"Compra de {quantity} acciones de {symbol} agregada.")
        else:
            st.error("Símbolo no encontrado en el archivo de acciones.")
    else:
        st.error("Por favor, ingrese un símbolo válido y una cantidad mayor a 0.")

# Sección para agregar nuevas ventas
st.subheader("➖ Agregar nueva venta")
symbol_venta = st.text_input("Símbolo de la acción a vender", key="symbol_venta")
quantity_venta = st.number_input("Cantidad de acciones a vender", min_value=1, step=1, key="quantity_venta")

if st.button("Agregar venta"):
    if symbol_venta and quantity_venta > 0:
        # Buscar los datos de la acción en el archivo de compras
        accion = df_compras[df_compras["Symbol"] == symbol_venta]
        if not accion.empty:
            current_quantity = accion.iloc[0]["Quantity"]
            if current_quantity >= quantity_venta:
                df_compras.loc[df_compras["Symbol"] == symbol_venta, "Quantity"] -= quantity_venta
                df_compras.loc[df_compras["Symbol"] == symbol_venta, "Total Investment"] -= accion.iloc[0]["Price"] * quantity_venta
                df_compras = df_compras[df_compras["Quantity"] > 0]  # Eliminar filas con cantidad 0
                df_compras.to_excel("compras.xlsx", index=False)
                st.success(f"Venta de {quantity_venta} acciones de {symbol_venta} registrada.")
            else:
                st.error("No tienes suficientes acciones para vender.")
        else:
            st.error("Símbolo no encontrado en el archivo de compras.")
    else:
        st.error("Por favor, ingrese un símbolo válido y una cantidad mayor a 0.")

# Calcular el porcentaje del portafolio
total_investment = df_compras["Total Investment"].sum()
df_compras["Portfolio Percentage"] = (df_compras["Total Investment"] / total_investment) * 100

# Guardar los datos actualizados en el archivo de compras
df_compras.to_excel("compras.xlsx", index=False)

# Mostrar las compras realizadas
st.subheader("💼 Acciones en tu portafolio")
st.dataframe(df_compras)

# Determinar acciones a vender: si ya no cumplen con el criterio de inversión
df_vender = df_compras[~df_compras["Symbol"].isin(df_recomendadas["Symbol"])]

st.subheader("⚠️ Acciones a vender")
st.dataframe(df_vender)

# Mostrar las recomendaciones
st.subheader("🔹 Acciones recomendadas para inversión")
st.dataframe(df_recomendadas)