import unittest
import pandas as pd
from datetime import datetime, timedelta
import ccxt
import time
from src import data, exchanges

class TestDataLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize test exchanges."""
        cls.exchange_dict = {}
        test_exchanges = ['bybit', 'mexc']  # Use two exchanges for testing
        
        for exchange_id in test_exchanges:
            try:
                config = {
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot',
                    },
                    'timeout': 30000,  # 30 seconds timeout
                    'rateLimit': 1000,  # Force 1 second between requests
                }
                exchange_class = getattr(ccxt, exchange_id)
                exchange = exchange_class(config)
                # Test connection and load markets
                exchange.load_markets()
                cls.exchange_dict[exchange_id] = exchange
                time.sleep(1)  # Wait between exchange initializations
            except Exception as e:
                print(f"Warning: Could not initialize {exchange_id}: {str(e)}")
                continue
        
        if not cls.exchange_dict:
            raise unittest.SkipTest("No exchanges could be initialized")

    def setUp(self):
        """Setup for each test."""
        if not self.exchange_dict:
            self.skipTest("No exchanges available")
        time.sleep(1)  # Rate limiting between tests

    def test_fetch_ohlcv(self):
        """Test OHLCV data fetching."""
        exchange = next(iter(self.exchange_dict.values()))  # Get first available exchange
        symbol = 'BTC/USDT'
        
        try:
            # Test data fetching
            df = data.fetch_ohlcv(exchange, symbol)
            
            # Skip if no data returned
            if df is None:
                self.skipTest("No data returned from exchange")
            
            # Verify DataFrame structure
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(len(df.columns), 6)  # timestamp, open, high, low, close, volume
            self.assertGreater(len(df), 0)  # At least some data points
            
            # Verify data types
            self.assertIsInstance(df['timestamp'].iloc[0], pd.Timestamp)
            self.assertIsInstance(df['close'].iloc[0], (float, int))
            self.assertIsInstance(df['volume'].iloc[0], (float, int))
            
            # Verify chronological order
            self.assertTrue(df['timestamp'].is_monotonic_increasing)
            
            # Verify no missing values
            self.assertFalse(df.isnull().any().any())
            
        except ccxt.NetworkError as e:
            self.skipTest(f"Network error: {str(e)}")
        except ccxt.ExchangeError as e:
            self.skipTest(f"Exchange error: {str(e)}")

    def test_find_arbitrage_opportunities(self):
        """Test arbitrage opportunity detection."""
        if len(self.exchange_dict) < 2:
            self.skipTest("Need at least 2 exchanges for arbitrage testing")
        
        selected_exchanges = list(self.exchange_dict.keys())[:2]
        min_volume = 1000  # Lower threshold for testing
        min_price_diff = 0.01  # Lower threshold for testing
        
        try:
            opportunities = data.find_arbitrage_opportunities(
                selected_exchanges,
                self.exchange_dict,
                min_volume,
                min_price_diff
            )
            
            # Verify opportunities structure
            self.assertIsInstance(opportunities, list)
            
            if opportunities:  # If any opportunities found
                opp = opportunities[0]
                
                # Verify opportunity data structure
                required_keys = {'symbol', 'exchange1', 'exchange2', 'price1', 
                               'price2', 'diff_percent', 'volume'}
                self.assertEqual(set(opp.keys()), required_keys)
                
                # Verify data types
                self.assertIsInstance(opp['symbol'], str)
                self.assertIsInstance(opp['exchange1'], str)
                self.assertIsInstance(opp['exchange2'], str)
                self.assertIsInstance(opp['price1'], (float, int))
                self.assertIsInstance(opp['price2'], (float, int))
                self.assertIsInstance(opp['diff_percent'], float)
                self.assertIsInstance(opp['volume'], (float, int))
                
                # Verify thresholds
                self.assertGreaterEqual(abs(opp['diff_percent']), min_price_diff)
                self.assertGreaterEqual(opp['volume'], min_volume)
                
                # Verify exchanges are different
                self.assertNotEqual(opp['exchange1'], opp['exchange2'])
                
        except ccxt.NetworkError as e:
            self.skipTest(f"Network error: {str(e)}")
        except ccxt.ExchangeError as e:
            self.skipTest(f"Exchange error: {str(e)}")

    def test_market_data_streaming(self):
        """Test continuous market data streaming."""
        exchange = next(iter(self.exchange_dict.values()))
        symbol = 'BTC/USDT'
        
        try:
            # Test multiple consecutive fetches
            data_points = []
            for _ in range(2):  # Reduced to 2 fetches to avoid rate limits
                df = data.fetch_ohlcv(exchange, symbol)
                if df is not None and not df.empty:
                    data_points.append(df['close'].iloc[-1])
                time.sleep(1)  # Rate limiting between fetches
            
            # Verify we got data each time
            self.assertGreater(len(data_points), 0)
            
        except ccxt.NetworkError as e:
            self.skipTest(f"Network error: {str(e)}")
        except ccxt.ExchangeError as e:
            self.skipTest(f"Exchange error: {str(e)}")

    def test_error_handling(self):
        """Test error handling in data fetching."""
        exchange = next(iter(self.exchange_dict.values()))
        
        # Test with invalid symbol
        df = data.fetch_ohlcv(exchange, 'INVALID/PAIR')
        self.assertIsNone(df)
        time.sleep(1)  # Rate limiting
        
        # Test with invalid timeframe
        df = data.fetch_ohlcv(exchange, 'BTC/USDT', timeframe='invalid')
        self.assertIsNone(df)
        time.sleep(1)  # Rate limiting
        
        # Test arbitrage with invalid exchange
        opportunities = data.find_arbitrage_opportunities(
            ['invalid_exchange'],
            {'invalid_exchange': None},
            100000,
            0.1
        )
        self.assertEqual(opportunities, [])

if __name__ == '__main__':
    unittest.main() 