from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, func
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuración de Flask y SQLAlchemy
app = Flask(__name__)
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/StocksApp"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Definición de modelos
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

# Rutas de la API
@app.route('/stocks', methods=['GET'])
def get_stocks():
    stocks = session.query(Stock).all()
    data = [{
        'Symbol': s.symbol,
        'Name': s.name,
        'Price': s.price,
        'BPS1': s.bps1,
        'BPS2': s.bps2,
        'BPS3': s.bps3,
        'BPS4': s.bps4,
        'P/E Actual': s.pe_actual,
        'P/E Histórico': s.pe_historico,
        'Recomendado': s.recomendado
    } for s in stocks]
    return jsonify(data)

@app.route('/compras', methods=['GET'])
def get_compras():
    compras = session.query(Compra).all()
    data = [{
        'Symbol': c.symbol,
        'Name': c.name,
        'Price': c.price,
        'Quantity': c.quantity,
        'Total Investment': c.total_investment,
        'Portfolio Percentage': c.portfolio_percentage
    } for c in compras]
    return jsonify(data)

@app.route('/compras', methods=['POST'])
def add_compra():
    data = request.json
    symbol = data.get('symbol')
    quantity = int(data.get('quantity'))

    if not symbol or quantity <= 0:
        return jsonify({'error': 'Datos inválidos'}), 400

    stock = session.query(Stock).filter_by(symbol=symbol).first()
    if not stock:
        return jsonify({'error': 'Símbolo no encontrado'}), 404

    compra = session.query(Compra).filter_by(symbol=symbol).first()
    price = stock.price
    total_investment = price * quantity

    if compra:
        compra.quantity += quantity
        compra.total_investment += total_investment
    else:
        compra = Compra(
            symbol=symbol, name=stock.name, price=price,
            quantity=quantity, total_investment=total_investment, portfolio_percentage=0
        )
        session.add(compra)

    # Calcular y actualizar el porcentaje del portafolio
    total_investment_all = session.query(Compra).with_entities(func.sum(Compra.total_investment)).scalar()
    for compra in session.query(Compra).all():
        if total_investment_all > 0:
            compra.portfolio_percentage = (compra.total_investment / total_investment_all) * 100
        else:
            compra.portfolio_percentage = 0

    session.commit()
    return jsonify({'message': 'Compra registrada'}), 201

@app.route('/ventas', methods=['POST'])
def sell_stock():
    data = request.json
    symbol = data.get('symbol')
    quantity = int(data.get('quantity'))

    if not symbol or quantity <= 0:
        return jsonify({'error': 'Datos inválidos'}), 400

    compra = session.query(Compra).filter_by(symbol=symbol).first()
    if not compra:
        return jsonify({'error': 'Símbolo no encontrado en portafolio'}), 404

    if compra.quantity < quantity:
        return jsonify({'error': 'No tienes suficientes acciones'}), 400

    compra.quantity -= quantity
    compra.total_investment -= compra.price * quantity
    if compra.quantity == 0:
        session.delete(compra)

    # Calcular y actualizar el porcentaje del portafolio
    total_investment_all = session.query(Compra).with_entities(func.sum(Compra.total_investment)).scalar()
    for compra in session.query(Compra).all():
        if total_investment_all > 0:
            compra.portfolio_percentage = (compra.total_investment / total_investment_all) * 100
        else:
            compra.portfolio_percentage = 0

    session.commit()
    return jsonify({'message': 'Venta registrada'}), 200

@app.route('/acciones-recomendadas', methods=['GET'])
def get_recommended():
    recomendadas = session.query(Stock).filter_by(recomendado=True).all()
    data = [{'Symbol': s.symbol, 'Name': s.name, 'Price': s.price} for s in recomendadas]
    return jsonify(data)
@app.route('/')
def home():
    return "¡Bienvenido a StocksApp! La API está funcionando."
if __name__ == '__main__':
    app.run(debug=True)
