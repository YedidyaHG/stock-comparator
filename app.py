import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# --- page config ---
st.set_page_config(page_title="Stock & Index Comparator", page_icon="📊", layout="wide")
st.title("📈 Stock & Index Comparator (Matplotlib Edition)")

# --- tickers selection ---
tickers = st.multiselect(
    "Select 2 or 3 stocks/indices",
    ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "^GSPC", "^IXIC", "^DJI"],
    default=["AAPL", "MSFT"]
)

# --- years range ---
years_range = st.slider(
    "Select range of years",
    min_value=2000,
    max_value=datetime.date.today().year,
    value=(2015, 2024)
)

start_date = f"{years_range[0]}-01-01"
end_date = f"{years_range[1]}-12-31"

# --- investment input ---
investment = st.number_input("Initial investment ($)", min_value=10, max_value=1000000, value=100, step=10)

# --- helpers ---
@st.cache_data
def get_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, progress=False)
    return df

@st.cache_data
def get_name(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get("shortName", ticker)
    except Exception:
        return ticker

def cumulative_return(df, investment):
    if df.empty:
        return None, None
    start_price = float(df["Close"].iloc[0])
    end_price = float(df["Close"].iloc[-1])
    ret = (end_price - start_price) / start_price * 100
    final_value = (end_price / start_price) * investment
    return round(ret, 2), round(final_value, 2)

# --- main ---
results = []
all_data = {}

if len(tickers) >= 2:
    for t in tickers:
        df = get_data(t, start_date, end_date)
        if not df.empty:
            all_data[t] = df
            ret, final_val = cumulative_return(df, investment)
            if ret is not None:
                results.append({
                    "Ticker": t,
                    "Company": get_name(t),
                    "Return %": ret,
                    f"Value of ${investment}": final_val
                })
        else:
            st.warning(f"No data found for {t}")

    # --- closing price chart ---
    if all_data:
        st.subheader(f"📊 Closing Prices {years_range[0]}–{years_range[1]}")
        fig, ax = plt.subplots(figsize=(10, 5))
        for t, df in all_data.items():
            ax.plot(df.index, df["Close"], label=t)
        ax.set_title("Closing Price Comparison")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price (USD)")
        ax.legend()
        st.pyplot(fig)

        # --- normalized chart ---
        st.subheader(f"📊 Normalized Prices (All start at $100) {years_range[0]}–{years_range[1]}")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        for t, df in all_data.items():
            normalized = df["Close"] / df["Close"].iloc[0] * 100
            ax2.plot(df.index, normalized, label=t)
        ax2.set_title("Normalized Price Comparison (Base = 100)")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Normalized Value (Base 100)")
        ax2.legend()
        st.pyplot(fig2)

    # --- returns table ---
    if results:
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values(by="Return %", ascending=False, ignore_index=True)
        st.subheader(f"🏆 Returns and Investment Value (${investment}) in {years_range[0]}–{years_range[1]}")
        st.dataframe(df_results)

else:
    st.warning("Please select at least 2 stocks/indices for comparison")
