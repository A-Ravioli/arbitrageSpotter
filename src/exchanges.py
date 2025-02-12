import ccxt
import streamlit as st

@st.cache_resource
def init_exchanges():
    """Initialize cryptocurrency exchanges with rate limiting enabled."""
    exchanges = {}
    # Selected exchanges that work well with public API access
    exchange_ids = [
        'mexc',       # Reliable public endpoints
        'gateio',     # Stable public API
        'huobi',      # Good market data access
        'okx',        # Solid public endpoints
        'phemex'      # Good for spot and derivatives
    ]
    
    for exchange_id in exchange_ids:
        try:
            config = {
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # Focus on spot markets
                }
            }
            
            exchange_class = getattr(ccxt, exchange_id)
            exchange = exchange_class(config)
            
            # Test the connection with a simple markets fetch
            exchange.load_markets()
            exchanges[exchange_id] = exchange
            
        except Exception as e:
            st.warning(f"Could not initialize {exchange_id}: {str(e)}")
            continue
            
    return exchanges

def setup_api_keys():
    """Setup API keys for exchanges that require them."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Exchange API Keys")
    
    # Store API keys in session state
    if 'exchange_keys' not in st.session_state:
        st.session_state.exchange_keys = {}
    
    # Add Coinbase with API key requirement
    with st.sidebar.expander("Coinbase API Keys"):
        coinbase_key = st.text_input("Coinbase API Key", type="password", key="coinbase_key")
        coinbase_secret = st.text_input("Coinbase Secret", type="password", key="coinbase_secret")
        
        if coinbase_key and coinbase_secret:
            st.session_state.exchange_keys['coinbase'] = {
                'apiKey': coinbase_key,
                'secret': coinbase_secret
            }
        elif 'coinbase' in st.session_state.exchange_keys:
            del st.session_state.exchange_keys['coinbase']

def fetch_markets(exchange):
    """Fetch all markets from an exchange."""
    try:
        return exchange.fetch_markets()
    except Exception as e:
        st.error(f"Error fetching markets from {exchange.id}: {str(e)}")
        return []

def fetch_ticker(exchange, symbol):
    """Fetch ticker data for a symbol from an exchange."""
    try:
        return exchange.fetch_ticker(symbol)
    except Exception as e:
        st.error(f"Error fetching ticker from {exchange.id} for {symbol}: {str(e)}")
        return None 