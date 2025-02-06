import aiohttp
import asyncio
import yfinance as yf
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# URL de Wikipedia con la lista de acciones del S&P 500
URL_SP500 = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

# Configuración de la base de datos
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/StocksApp"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

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

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

async def fetch_sp500_symbols():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL_SP500) as response:
                html = await response.text()
                return html
    except Exception as e:
        logging.error(f"Error al obtener la lista de símbolos del S&P 500: {e}")
        return None

async def main():
    html = await fetch_sp500_symbols()
    if not html:
        logging.error("No se pudo obtener la lista de símbolos del S&P 500.")
        return

    soup = BeautifulSoup(html, 'html.parser')
    tabla = soup.find('table')

    if not tabla:
        logging.error("No se encontró la tabla en la página de Wikipedia.")
        return

    filas = tabla.find_all('tr')
    for fila in filas[1:]:
        celdas = fila.find_all('td')
        if len(celdas) > 1:
            symbol = celdas[0].text.strip()
            name = celdas[1].text.strip()
            if not session.query(Stock).filter_by(symbol=symbol).first():
                stock = Stock(symbol=symbol, name=name)
                session.add(stock)

    session.commit()

    for stock in session.query(Stock).all():
        logging.info(f'🔍 Buscando datos para {stock.symbol}...')

        try:
            yf_stock = yf.Ticker(stock.symbol)
            price = float(yf_stock.history(period="1d")['Close'].iloc[-1])
            stock.price = price
            logging.info(f'✅ {stock.symbol} - Precio: {price}')

            earnings = [float(eps) for eps in yf_stock.financials.loc['Diluted EPS'].dropna().tolist()[:5]]
            if len(earnings) >= 4:
                stock.bps1, stock.bps2, stock.bps3, stock.bps4 = earnings[:4]
            logging.info(f'✅ {stock.symbol} - EPS Históricos: {earnings}')

            stock.pe_actual = float(yf_stock.info.get("trailingPE", "N/A"))
            logging.info(f'✅ {stock.symbol} - P/E Actual: {stock.pe_actual}')

            pe_historico = []
            for eps in earnings:
                if eps > 0:
                    pe_historico.append(price / eps)
            if pe_historico:
                stock.pe_historico = sum(pe_historico) / len(pe_historico)
            else:
                stock.pe_historico = None
            logging.info(f'✅ {stock.symbol} - P/E Histórico: {stock.pe_historico}')

        except Exception as e:
            logging.error(f'❌ Error al obtener datos de {stock.symbol}: {e}')

    session.commit()
    logging.info('\n✅ Proceso completado. Datos guardados en la base de datos.')

if __name__ == "__main__":
    asyncio.run(main())
