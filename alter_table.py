from sqlalchemy import create_engine

# Configuración de la base de datos
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/StocksApp"
engine = create_engine(DATABASE_URL)

# Agregar la columna 'recomendado' a la tabla 'stocks'
with engine.connect() as connection:
    connection.execute('ALTER TABLE stocks ADD COLUMN IF NOT EXISTS recomendado BOOLEAN DEFAULT FALSE')
