import pandas as pd
import streamlit as st
import ccxt
from . import exchanges
import time

def fetch_ohlcv(exchange, symbol, timeframe='1m', limit=60):
    """Fetch OHLCV data for a symbol from an exchange."""
    try:
        # Verify the symbol exists on the exchange
        markets = exchange.load_markets()
        if symbol not in markets:
            st.error(f"Symbol {symbol} not found on {exchange.id}")
            return None
            
        # Fetch OHLCV data
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        # Check if we got any data
        if not ohlcv:
            st.warning(f"No OHLCV data returned for {symbol} on {exchange.id}")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Verify data quality
        if df.empty or df.isnull().any().any():
            st.warning(f"Invalid data received for {symbol} on {exchange.id}")
            return None
            
        return df
        
    except ccxt.NetworkError as e:
        st.error(f"Network error fetching data from {exchange.id}: {str(e)}")
        return None
    except ccxt.ExchangeError as e:
        st.error(f"Exchange error for {exchange.id}: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error fetching data from {exchange.id}: {str(e)}")
        return None

def find_arbitrage_opportunities(selected_exchanges, exchanges_dict, min_volume, min_price_diff):
    """Find arbitrage opportunities between selected exchanges."""
    opportunities = []
    
    for exchange1 in selected_exchanges:
        for exchange2 in selected_exchanges:
            if exchange1 >= exchange2:
                continue
                
            try:
                # Get exchange instances
                ex1 = exchanges_dict.get(exchange1)
                ex2 = exchanges_dict.get(exchange2)
                
                if not ex1 or not ex2:
                    continue
                    
                # Fetch markets with rate limiting
                markets1 = exchanges.fetch_markets(ex1)
                time.sleep(1)  # Rate limiting
                markets2 = exchanges.fetch_markets(ex2)
                time.sleep(1)  # Rate limiting
                
                if not markets1 or not markets2:
                    continue
                
                # Find common symbols
                common_symbols = set(m['symbol'] for m in markets1 if m['active']) & \
                               set(m['symbol'] for m in markets2 if m['active'])
                
                for symbol in common_symbols:
                    try:
                        # Fetch tickers with rate limiting
                        ticker1 = exchanges.fetch_ticker(ex1, symbol)
                        time.sleep(1)  # Rate limiting
                        ticker2 = exchanges.fetch_ticker(ex2, symbol)
                        time.sleep(1)  # Rate limiting
                        
                        if (ticker1 and ticker2 and 
                            ticker1.get('bid') and ticker2.get('ask') and 
                            ticker1.get('quoteVolume', 0) > min_volume):
                            
                            price_diff = ((ticker1['bid'] - ticker2['ask']) / ticker2['ask']) * 100
                            
                            if abs(price_diff) >= min_price_diff:
                                opportunities.append({
                                    'symbol': symbol,
                                    'exchange1': exchange1,
                                    'exchange2': exchange2,
                                    'price1': ticker1['bid'],
                                    'price2': ticker2['ask'],
                                    'diff_percent': price_diff,
                                    'volume': ticker1['quoteVolume']
                                })
                    except (ccxt.NetworkError, ccxt.ExchangeError) as e:
                        st.warning(f"Error fetching {symbol} data: {str(e)}")
                        continue
                        
            except Exception as e:
                st.error(f"Error comparing {exchange1} and {exchange2}: {str(e)}")
                continue
                
    return opportunities 