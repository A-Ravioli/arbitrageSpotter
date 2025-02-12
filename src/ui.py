import streamlit as st

# Add default tokens at the top
DEFAULT_TOKENS = [
    'BTC/USDT',
    'ETH/USDT',
    'BNB/USDT',
    'SOL/USDT',
    'XRP/USDT',
    'DOGE/USDT',
    'ADA/USDT',
    'AVAX/USDT',
    'DOT/USDT',
    'MATIC/USDT',
    'LINK/USDT',
    'UNI/USDT',
    'AAVE/USDT',
    'ATOM/USDT',
]

def apply_theme():
    """Apply dark theme to the Streamlit app."""
    st.markdown("""
        <style>
            /* Main theme */
            .stApp {
                background-color: #131722;
                color: #d1d4dc;
            }
            
            /* Sidebar */
            [data-testid="stSidebar"] {
                background-color: #1e222d;
                border-left: 1px solid #2a2e39;
            }
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 2px;
                background-color: #1e222d;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                background-color: #1e222d;
                border-radius: 4px 4px 0px 0px;
                gap: 1px;
                color: #d1d4dc;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: #2962ff;
            }
            
            /* Search bar */
            .stTextInput input {
                background-color: #2a2e39;
                color: #d1d4dc;
                border: 1px solid #363c4e;
            }
            
            /* Buttons */
            .stButton>button {
                color: #d1d4dc;
                background-color: #2a2e39;
                border: 1px solid #363c4e;
            }
            
            /* Charts area */
            [data-testid="stMetric"] {
                background-color: #1e222d;
                padding: 10px;
                border-radius: 4px;
            }
            
            /* Cards */
            div[data-testid="stHorizontalBlock"] > div {
                background-color: #1e222d;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #2a2e39;
            }
            
            /* Watchlist items */
            div.watchlist-item {
                background-color: #1e222d;
                padding: 10px;
                margin: 5px 0;
                border-radius: 4px;
                border: 1px solid #2a2e39;
            }
            
            /* Price changes */
            .price-up {
                color: #26a69a;
            }
            .price-down {
                color: #ef5350;
            }
        </style>
    """, unsafe_allow_html=True)

def setup_watchlist():
    """Setup and manage the watchlist."""
    if 'watchlist' not in st.session_state:
        # Initialize with default tokens
        st.session_state.watchlist = set(DEFAULT_TOKENS)
    if 'available_tokens' not in st.session_state:
        st.session_state.available_tokens = set()

def add_to_watchlist(symbol):
    """Add a symbol to the watchlist."""
    st.session_state.watchlist.add(symbol)
    st.session_state.available_tokens.add(symbol)  # Remember this token exists

def remove_from_watchlist(symbol):
    """Remove a symbol from the watchlist."""
    st.session_state.watchlist.discard(symbol)

def manage_watchlist():
    """Display watchlist management interface."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Add new token
        new_token = st.text_input("Add Token (e.g., BTC/USDT)", key="new_token")
        if st.button("Add Token") and new_token:
            add_to_watchlist(new_token.upper())
            st.experimental_rerun()
    
    with col2:
        # Quick add from common tokens
        if st.button("Add Common Tokens"):
            for token in DEFAULT_TOKENS:
                add_to_watchlist(token)
            st.experimental_rerun()
    
    # Display all available tokens for quick add
    st.markdown("### Quick Add")
    available = sorted(st.session_state.available_tokens - st.session_state.watchlist)
    if available:
        cols = st.columns(4)
        for i, token in enumerate(available):
            with cols[i % 4]:
                if st.button(f"+ {token}", key=f"add_{token}"):
                    add_to_watchlist(token)
                    st.experimental_rerun()

def display_watchlist_item(symbol, price, change_24h):
    """Display a single watchlist item."""
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    
    with col1:
        st.write(symbol)
    with col2:
        st.write(f"${price:,.2f}")
    with col3:
        color = "price-up" if change_24h >= 0 else "price-down"
        st.markdown(f'<span class="{color}">{change_24h:+.2f}%</span>', unsafe_allow_html=True)
    with col4:
        if st.button("❌", key=f"remove_{symbol}"):
            remove_from_watchlist(symbol)
            st.experimental_rerun()

def display_arbitrage_opportunity(opp):
    """Display a single arbitrage opportunity."""
    color = "price-up" if opp['diff_percent'] > 0 else "price-down"
    st.markdown(f"""
        <div style='padding: 10px; background-color: #1e222d; border-radius: 4px; margin: 5px 0; border: 1px solid #2a2e39;'>
            <div style='display: flex; justify-content: space-between;'>
                <h4>{opp['symbol']}</h4>
                <span class='{color}'>{opp['diff_percent']:.2f}%</span>
            </div>
            <p>{opp['exchange1'].title()} vs {opp['exchange2'].title()}</p>
            <div style='display: flex; justify-content: space-between;'>
                <span>${opp['price1']:,.2f}</span>
                <span>${opp['price2']:,.2f}</span>
            </div>
            <p style='color: #848e9c;'>Volume: ${opp['volume']:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)

def setup_sidebar(exchange_list):
    """Setup the sidebar with controls."""
    st.sidebar.title("Settings")
    
    selected_exchanges = st.sidebar.multiselect(
        "Select Exchanges",
        options=exchange_list,
        default=exchange_list[:2]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    
    min_volume = st.sidebar.number_input(
        "Minimum 24h Volume (USD)",
        min_value=0,
        value=1000000,
        step=100000,
        format="%d"
    )
    
    min_price_diff = st.sidebar.number_input(
        "Minimum Price Difference (%)",
        min_value=0.0,
        value=1.0,
        step=0.1,
        format="%.1f"
    )
    
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 30)
    
    return selected_exchanges, min_volume, min_price_diff, auto_refresh, refresh_interval 