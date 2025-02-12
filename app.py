import streamlit as st
import time
from src import exchanges, data, visualization, ui

# Set page config for dark theme
st.set_page_config(
    page_title="Crypto Arbitrage Spotter",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize app
ui.apply_theme()
ui.setup_watchlist()

# Initialize exchanges
with st.spinner("Initializing exchanges..."):
    exchange_dict = exchanges.init_exchanges()

if not exchange_dict:
    st.error("No exchanges could be initialized. Please try again later.")
    st.stop()

# Setup sidebar
selected_exchanges, min_volume, min_price_diff, auto_refresh, refresh_interval = ui.setup_sidebar(
    list(exchange_dict.keys())
)

if len(selected_exchanges) < 2:
    st.warning("Please select at least 2 exchanges to find arbitrage opportunities.")
    st.stop()

# Main content area (70% width)
main_col, right_col = st.columns([0.7, 0.3])

with main_col:
    # Search bar
    search_col, time_col = st.columns([0.7, 0.3])
    with search_col:
        symbol_search = st.text_input("🔍", placeholder="Search symbol (e.g. BTC/USDT)")
        if symbol_search:
            ui.add_to_watchlist(symbol_search.upper())  # Add searched tokens to available list
    with time_col:
        st.text(f"Last updated: {time.strftime('%H:%M:%S')}")
    
    # Chart area
    if symbol_search:
        st.subheader(f"Price Chart: {symbol_search}")
        with st.spinner("Loading price chart..."):
            visualization.plot_multi_exchange_comparison(
                symbol_search,
                selected_exchanges,
                exchange_dict
            )
    else:
        st.info("Enter a symbol to view price charts")

# Right sidebar (30% width)
with right_col:
    tab1, tab2, tab3 = st.tabs(["💹 Arbitrage", "📊 Watchlist", "⚙️ Manage"])
    
    # Arbitrage tab
    with tab1:
        with st.spinner("Finding arbitrage opportunities..."):
            opportunities = data.find_arbitrage_opportunities(
                selected_exchanges,
                exchange_dict,
                min_volume,
                min_price_diff
            )
        
        if not opportunities:
            st.info("No arbitrage opportunities found matching your criteria.")
        else:
            opportunities.sort(key=lambda x: abs(x['diff_percent']), reverse=True)
            for opp in opportunities:
                ui.display_arbitrage_opportunity(opp)
                if symbol_search != opp['symbol']:
                    if st.button(f"📈 View {opp['symbol']}", key=f"view_{opp['symbol']}"):
                        symbol_search = opp['symbol']
                        st.experimental_rerun()
    
    # Watchlist tab
    with tab2:
        st.subheader("Watchlist")
        for symbol in sorted(st.session_state.watchlist):
            try:
                # Get price data from first available exchange
                exchange = exchange_dict[selected_exchanges[0]]
                ticker = exchange.fetch_ticker(symbol)
                if ticker:
                    ui.display_watchlist_item(
                        symbol,
                        ticker['last'],
                        ticker['percentage']
                    )
            except Exception as e:
                st.error(f"Error fetching data for {symbol}: {str(e)}")
    
    # Manage tab
    with tab3:
        st.subheader("Manage Watchlist")
        ui.manage_watchlist()

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.experimental_rerun() 