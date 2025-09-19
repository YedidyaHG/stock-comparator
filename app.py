import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import datetime

# --- הגדרות ראשיות ---
st.set_page_config(page_title="Stocks & ETFs Comparator", page_icon="📊", layout="wide")
st.title("📈 Stocks, Indices & ETFs Comparator")

DEFAULT_INVESTMENT = 100

# --- Sidebar ---
st.sidebar.header("Options")

tickers = st.sidebar.text_input(
    "Enter tickers (comma separated):",
    "AAPL, MSFT, TSLA, SPY, ^GSPC"
)
tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]

# טווח שנים
years_range = st.sidebar.slider(
    "Select range of years:",
    min_value=1980,
    max_value=datetime.date.today().year,
    value=(2015, 2024)
)
start_date = f"{years_range[0]}-01-01"
end_date = f"{years_range[1]}-12-31"

investment = st.sidebar.number_input("Initial investment ($)", min_value=10, value=DEFAULT_INVESTMENT, step=10)

# --- Helper functions ---
@st.cache_data
def get_stock_data(ticker, start, end):
    return yf.download(ticker, start=start, end=end, progress=False)

def calc_return(df, investment):
    if df.empty:
        return None, None
    start_price = float(df["Close"].iloc[0])
    end_price = float(df["Close"].iloc[-1])
    ret = (end_price - start_price) / start_price * 100
    final_value = (end_price / start_price) * investment
    return round(ret, 2), round(final_value, 2)

# --- Main ---
all_data = {}
results = []

for t in tickers:
    df = get_stock_data(t, start_date, end_date)
    if not df.empty:
        all_data[t] = df
        ret, val = calc_return(df, investment)
        results.append({"Ticker": t, "Return %": ret, f"Value of ${investment}": val})
    else:
        st.warning(f"No data for {t}")

if all_data:
    # --- גרף מחירים ---
    st.subheader("Stock/ETF Prices")
    fig = go.Figure()
    for t, df in all_data.items():
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name=t))
    fig.update_layout(title="Closing Prices", xaxis_title="Date", yaxis_title="Price (USD)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # --- גרף מנורמל ---
    st.subheader("Normalized Prices (Base = 100)")
    fig_norm = go.Figure()
    for t, df in all_data.items():
        norm = df["Close"] / df["Close"].iloc[0] * 100
        fig_norm.add_trace(go.Scatter(x=df.index, y=norm, mode="lines", name=t))
    fig_norm.update_layout(title="Normalized Price Comparison", xaxis_title="Date", yaxis_title="Index (Base 100)",
                           hovermode="x unified")
    st.plotly_chart(fig_norm, use_container_width=True)

    # --- טבלה ---
    if results:
        df_results = pd.DataFrame(results).sort_values(by="Return %", ascending=False, ignore_index=True)
        st.subheader("🏆 Performance Table")
        st.dataframe(df_results)
