import pandas as pd
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from plyer import notification
import yfinance as yf

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

# Función para obtener el valor del VIX usando yfinance
def obtener_valor_vix():
    try:
        vix = yf.Ticker("^VIX")
        vix_value = vix.history(period="1d")["Close"].iloc[-1]
        return float(vix_value)
    except Exception as e:
        print(f"Error al obtener el valor del VIX: {e}")
        return None

# Verificar el valor del VIX y enviar notificación si supera 25
vix_value = obtener_valor_vix()
if vix_value and vix_value > 25:
    notification.notify(
        title="Alerta de VIX",
        message=f"El índice VIX ha superado 25. Valor actual: {vix_value}",
        timeout=10
    )

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

# Verificar los datos cargados
print("Datos cargados:")
print(df.head())

# Aplicar condiciones de inversión
df_recomendadas = df[
    (df['BPS1'] / df['BPS4'] > 1.5) &  # Crecimiento de 1.5x en 4 años
    (df['BPS1'] > df['BPS2']) &
    (df['BPS2'] > df['BPS3']) &
    (df['BPS3'] > df['BPS4'])  # Tendencia creciente del BPS
]

# Verificar las condiciones aplicadas
print("Condiciones aplicadas:")
print(df_recomendadas.head())

# Guardar las acciones recomendadas en la base de datos
for idx, row in df_recomendadas.iterrows():
    stock = session.query(Stock).filter_by(symbol=row['Symbol']).first()
    if stock:
        stock.recomendado = True
session.commit()

# Listas para notificaciones
acciones_comprar = []
acciones_vender = []

# Determinar acciones a comprar
for idx, row in df_recomendadas.iterrows():
    pe_actual = row["P/E Actual"]
    pe_historico = row["P/E Histórico"]
    if pd.notna(pe_actual) and pd.notna(pe_historico) and (pe_actual * 2 < pe_historico):
        acciones_comprar.append(row['Symbol'])

# Cargar el archivo de compras para determinar acciones a vender
compras = session.query(Compra).all()
df_compras = pd.DataFrame([{
    'Symbol': compra.symbol,
    'Name': compra.name,
    'Price': compra.price,
    'Quantity': compra.quantity,
    'Total Investment': compra.total_investment,
    'Portfolio Percentage': compra.portfolio_percentage
} for compra in compras])

# Determinar acciones a vender
for idx, row in df_compras.iterrows():
    pe_actual = df.loc[df["Symbol"] == row["Symbol"], "P/E Actual"].values[0]
    pe_historico = df.loc[df["Symbol"] == row["Symbol"], "P/E Histórico"].values[0]
    if pd.notna(pe_actual) and pd.notna(pe_historico) and (pe_actual * 1.5 > pe_historico):
        acciones_vender.append(row['Symbol'])

# Enviar notificación de acciones a comprar
if acciones_comprar:
    notification.notify(
        title="Acciones recomendadas para compra",
        message=f"Las siguientes acciones deberían comprarse: {', '.join(acciones_comprar)}",
        timeout=10
    )

# Enviar notificación de acciones a vender
if acciones_vender:
    notification.notify(
        title="Acciones recomendadas para venta",
        message=f"Las siguientes acciones deberían venderse: {', '.join(acciones_vender)}",
        timeout=10
    )

# Mostrar las acciones recomendadas
print("📊 Acciones recomendadas para inversión:")
print(df_recomendadas[['Symbol', 'Name', 'Price', 'BPS1', 'BPS2', 'BPS3', 'BPS4', 'P/E Actual', 'P/E Histórico']])
