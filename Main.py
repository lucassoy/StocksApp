import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

st.set_page_config(layout="wide")

# Configuración de la base de datos
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/StocksApp"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float)
    bps1 = Column(Float)
    bps2 = Column(Float)
    bps3 = Column(Float)
    bps4 = Column(Float)
    pe_actual = Column(Float)
    pe_historico = Column(Float)
    recomendado = Column(Boolean, default=False)

class Compra(Base):
    __tablename__ = 'compras'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float)
    quantity = Column(Integer)
    total_investment = Column(Float)
    portfolio_percentage = Column(Float)

Base.metadata.create_all(engine)

# Cargar datos desde la base de datos
stocks = session.query(Stock).all()
df = pd.DataFrame([{
    'Symbol': stock.symbol,
    'Name': stock.name,
    'Price': stock.price,
    'BPS1': stock.bps1,
    'BPS2': stock.bps2,
    'BPS3': stock.bps3,
    'BPS4': stock.bps4,
    'P/E Actual': stock.pe_actual,
    'P/E Histórico': stock.pe_historico
} for stock in stocks])

try:
    df_recomendadas = df[df['recomendado'] == True]
except KeyError:
    st.error("No se encontraron recomendaciones. Asegúrate de que se hayan generado correctamente.")
    df_recomendadas = pd.DataFrame()

compras = session.query(Compra).all()
df_compras = pd.DataFrame([{
    'Symbol': compra.symbol,
    'Name': compra.name,
    'Price': compra.price,
    'Quantity': compra.quantity,
    'Total Investment': compra.total_investment,
    'Portfolio Percentage': compra.portfolio_percentage
} for compra in compras])

st.title("📊 Análisis de Acciones")

col1, col2 = st.columns(2)

with col1:
    st.subheader("➕ Agregar nueva compra")
    symbol = st.text_input("Símbolo de la acción", key="symbol_compra")
    quantity = st.number_input("Cantidad de acciones", min_value=1, step=1, key="quantity_compra")

    if st.button("Agregar compra"):
        if symbol and quantity > 0:
            accion = df[df["Symbol"] == symbol]
            if not accion.empty:
                name = accion.iloc[0]["Name"]
                price = accion.iloc[0]["Price"]
                total_investment = price * quantity
                compra = session.query(Compra).filter_by(symbol=symbol).first()
                if compra:
                    compra.quantity += quantity
                    compra.total_investment += total_investment
                else:
                    new_compra = Compra(
                        symbol=symbol,
                        name=name,
                        price=price,
                        quantity=quantity,
                        total_investment=total_investment,
                        portfolio_percentage=0
                    )
                    session.add(new_compra)
                session.commit()
                st.success(f"Compra de {quantity} acciones de {symbol} agregada.")
            else:
                st.error("Símbolo no encontrado en la base de datos.")
        else:
            st.error("Por favor, ingrese un símbolo válido y una cantidad mayor a 0.")

with col2:
    st.subheader("➖ Agregar nueva venta")
    symbol_venta = st.text_input("Símbolo de la acción a vender", key="symbol_venta")
    quantity_venta = st.number_input("Cantidad de acciones a vender", min_value=1, step=1, key="quantity_venta")

    if st.button("Agregar venta"):
        if symbol_venta and quantity_venta > 0:
            compra = session.query(Compra).filter_by(symbol=symbol_venta).first()
            if compra:
                if compra.quantity >= quantity_venta:
                    compra.quantity -= quantity_venta
                    compra.total_investment -= compra.price * quantity_venta
                    if compra.quantity == 0:
                        session.delete(compra)
                    session.commit()
                    st.success(f"Venta de {quantity_venta} acciones de {symbol_venta} registrada.")
                else:
                    st.error("No tienes suficientes acciones para vender.")
            else:
                st.error("Símbolo no encontrado en el archivo de compras.")
        else:
            st.error("Por favor, ingrese un símbolo válido y una cantidad mayor a 0.")

total_investment = df_compras["Total Investment"].sum()
for compra in session.query(Compra).all():
    compra.portfolio_percentage = (compra.total_investment / total_investment) * 100
session.commit()

st.subheader("💼 Acciones en tu portafolio")
st.dataframe(df_compras)

df_vender = df_compras[~df_compras["Symbol"].isin(df_recomendadas["Symbol"])]

st.subheader("⚠️ Acciones a vender")
st.dataframe(df_vender)

st.subheader("🔹 Acciones recomendadas para inversión")
st.dataframe(df_recomendadas)