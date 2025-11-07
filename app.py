import streamlit as st
from BinomialPricer import OptionBinomial as option

KEY=st.secrets["KEY"]

def price_and_delta(r,ticker,initial_price,strike,time_to_maturity,div_yield,side,steps):
    o = option(KEY,r,ticker,initial_price,strike,time_to_maturity,div_yield,side,steps)
    return o.get_V0(),o.get_delta()

# --- Page config --------------------------------------------------------------
st.set_page_config(page_title="Option Pricer (Price & Delta)", page_icon="📊")

st.title("📊 Option Pricer — Price & Delta")
st.caption("Sidebar for inputs → click Render → see results on the right.")

# --- Sidebar inputs -----------------------------------------------------------
st.sidebar.header("Parameters")

ticker = st.sidebar.text_input("Ticker", value="AAPL")
side = st.sidebar.selectbox("Option Side", options=["call", "put"], index=0)

c1, c2 = st.sidebar.columns(2)
with c1:
    S0 = st.number_input("Spot Price S₀", min_value=0.0, value=190.0, step=0.01, format="%.2f")
    T = st.number_input("Days to maturity", min_value=7, value=7, step=1)
    steps = st.number_input("Binomial Steps", min_value=5, value=10, step=1)
with c2:
    K = st.number_input("Strike K", min_value=0.0, value=190.0, step=0.25, format="%.2f")
    r = st.number_input("Risk-free r (annual)", min_value=-1.0, value=0.050000, step=0.01, format="%.2f")
    q = st.number_input("Dividend Yield q (decimal)", min_value=0.0, value=0.000000, step=0.0001, format="%.4f")

render = st.sidebar.button("Render")

if render:
    if price_and_delta is None:
        st.stop()
    try:
        price, delta = price_and_delta(
            r=r,
            ticker=ticker,
            initial_price=S0,
            strike=K,
            time_to_maturity=T/365,
            div_yield=q,
            side=side,
            steps=int(steps),
        )

        st.subheader("Results")
        m1, m2 = st.columns(2)
        m1.metric("Price (V₀)", f"{price:,.6f}")
        m2.metric("Delta (∂V/∂S)", f"{delta:,.6f}")

        with st.expander("Inputs (echo)"):
            st.json(
                {
                    "ticker": ticker,
                    "side": side,
                    "S0": S0,
                    "K": K,
                    "T": T,
                    "r": r,
                    "q": q,
                    "steps": int(steps),
                }
            )
    except Exception as e:
        st.error(f"Computation failed: {e}")
else:
    st.info("Set parameters in the left sidebar, then click **Render** to compute price and delta.")
