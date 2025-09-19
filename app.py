import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import datetime

# --- Page Config ---
st.set_page_config(page_title="Stock & Index Comparator", page_icon="📊", layout="wide")
st.title("📈 Stock & Index Comparator – Advanced Edition")

# --- Presets ---
TOP_10_STOCKS = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]
INDICES = ["^GSPC", "^IXIC", "^DJI"]

# --- Sidebar Options ---
st.sidebar.header("Options")

mode = st.sidebar.radio("Choose dataset:", ["Custom Stocks", "Top 10 Stocks", "Indices"])

if mode == "Custom Stocks":
    tickers = st.sidebar.text_input("Enter tickers (comma separated):", "AAPL, MSFT, TSLA")
    tickers = [t.strip().upper() for t in tickers.split(",") if t.strip() != ""]
elif mode == "Top 10 Stocks":
    tickers = st.sidebar.multiselect("Select from Top 10", TOP_10_STOCKS, default=["AAPL", "MSFT"])
elif mode == "Indices":
    tickers = st.sidebar.multiselect("Select Indices", INDICES, default=["^GSPC", "^IXIC"])

# --- Time Range ---
years_mode = st.sidebar.radio("Select period:", ["Single Year", "Year Range"])

if years_mode == "Single Year":
    year = st.sidebar.number_input("Year:", min_value=1980, max_value=datetime.date.today().year, value=2020)
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
else:
    years_range = st.sidebar.slider("Select range of years:", min_value=1980,
                                    max_value=datetime.date.today().year,
                                    value=(2015, 2024))
    start_date = f"{years_range[0]}-01-01"
    end_date = f"{years_range[1]}-12-31"

# --- Investment ---
investment = st.sidebar.number_input("Initial investment ($)", min_value=10, max_value=1000000, value=100, step=10)

# --- Helpers ---
@st.cache_data
def get_data(ticker, start, end):
    return yf.download(ticker, start=start, end=end, progress=False)

def cumulative_return(df, investment):
    if df.empty:
        return None, None
    start_price = float(df["Close"].iloc[0])
    end_price = float(df["Close"].iloc[-1])
    ret = (end_price - start_price) / start_price * 100
    final_value = (end_price / start_price) * investment
    return round(ret, 2), round(final_value, 2)

# --- Data Processing ---
results = []
all_data = {}

if len(tickers) >= 1:
    for t in tickers:
        df = get_data(t, start_date, end_date)
        if not df.empty:
            all_data[t] = df
            ret, final_val = cumulative_return(df, investment)
            if ret is not None:
                results.append({
                    "Ticker": t,
                    "Return %": ret,
                    f"Value of ${investment}": final_val
                })
        else:
            st.warning(f"No data found for {t}")

    # --- Closing Prices Chart ---
    if all_data:
        st.subheader("📊 Closing Prices")
        fig = go.Figure()
        for t, df in all_data.items():
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name=t))
        fig.update_layout(
            title="Closing Price Comparison",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- Normalized Chart ---
        st.subheader("📊 Normalized Prices (Base = 100)")
        fig2 = go.Figure()
        for t, df in all_data.items():
            normalized = df["Close"] / df["Close"].iloc[0] * 100
            fig2.add_trace(go.Scatter(x=df.index, y=normalized, mode="lines", name=t))
        fig2.update_layout(
            title="Normalized Price Comparison",
            xaxis_title="Date",
            yaxis_title="Normalized Value (Base 100)",
            hovermode="x unified"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- Results Table ---
    if results:
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values(by="Return %", ascending=False, ignore_index=True)
        st.subheader("🏆 Performance Table")
        st.dataframe(df_results)

else:
    st.warning("Please select at least one ticker")
