import aiohttp
import asyncio
from openpyxl import Workbook, load_workbook
import yfinance as yf
from bs4 import BeautifulSoup

# URL de Wikipedia con la lista de acciones del S&P 500
URL_SP500 = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

async def fetch_sp500_symbols():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL_SP500) as response:
            html = await response.text()
            return html

async def main():
    html = await fetch_sp500_symbols()
    soup = BeautifulSoup(html, 'html.parser')
    tabla = soup.find('table')

    if not tabla:
        raise Exception("No se encontró la tabla en la página de Wikipedia.")

    filas = tabla.find_all('tr')
    datos = [["Symbol", "Name"]]
    for fila in filas[1:]:
        celdas = fila.find_all('td')
        if len(celdas) > 1:
            symbol = celdas[0].text.strip()
            name = celdas[1].text.strip()
            datos.append([symbol, name])

    wb = Workbook()
    ws = wb.active
    for row in datos:
        ws.append(row)

    ws.cell(row=1, column=3, value='Price')
    ws.cell(row=1, column=4, value='BPS1')
    ws.cell(row=1, column=5, value='BPS2')
    ws.cell(row=1, column=6, value='BPS3')
    ws.cell(row=1, column=7, value='BPS4')
    ws.cell(row=1, column=8, value='P/E Actual')
    ws.cell(row=1, column=9, value='P/E Histórico')

    wb.save('acciones.xlsx')

    wb = load_workbook('acciones.xlsx')
    ws = wb.active

    for idx, row in enumerate(ws.iter_rows(min_row=2, min_col=1, max_col=1, values_only=True), start=2):
        symbol = row[0]
        print(f'🔍 Buscando datos para {symbol}...')

        try:
            stock = yf.Ticker(symbol)
            price = stock.history(period="1d")['Close'].iloc[-1]
            ws.cell(row=idx, column=3, value=price)
            print(f'✅ {symbol} - Precio: {price}')

            earnings = stock.financials.loc['Diluted EPS'].dropna().tolist()[:5]
            for i, eps in enumerate(earnings):
                ws.cell(row=idx, column=4 + i, value=eps)
            print(f'✅ {symbol} - EPS Históricos: {earnings}')

            pe_actual = stock.info.get("trailingPE", "N/A")
            ws.cell(row=idx, column=8, value=pe_actual)
            print(f'✅ {symbol} - P/E Actual: {pe_actual}')

            pe_historico = []
            for i, eps in enumerate(earnings):
                if eps > 0:
                    pe_historico.append(price / eps)
            if pe_historico:
                pe_historico_avg = sum(pe_historico) / len(pe_historico)
            else:
                pe_historico_avg = "N/A"
            ws.cell(row=idx, column=9, value=pe_historico_avg)
            print(f'✅ {symbol} - P/E Histórico: {pe_historico_avg}')

        except Exception as e:
            print(f'❌ Error al obtener datos de {symbol}: {e}')

    wb.save('acciones.xlsx')
    print('\n✅ Proceso completado. Datos guardados en "acciones.xlsx".')

if __name__ == "__main__":
    asyncio.run(main())
