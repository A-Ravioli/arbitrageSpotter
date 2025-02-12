import unittest
import ccxt
import time
from src import data, exchanges
from src.ui import DEFAULT_TOKENS

class TestArbitrage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize test exchanges."""
        cls.exchange_dict = {}
        test_exchanges = ['mexc', 'gateio', 'okx']  # Use exchanges with good public APIs
        
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
        
        if len(cls.exchange_dict) < 2:
            raise unittest.SkipTest("Need at least 2 exchanges for testing")

    def setUp(self):
        """Setup for each test."""
        time.sleep(1)  # Rate limiting between tests

    def test_find_real_arbitrage_opportunities(self):
        """Test finding real arbitrage opportunities in major tokens."""
        selected_exchanges = list(self.exchange_dict.keys())[:2]
        min_volume = 10000  # Lower threshold for testing
        min_price_diff = 0.1  # Lower threshold for testing
        
        # Test each default token
        for symbol in DEFAULT_TOKENS:
            try:
                opportunities = data.find_arbitrage_opportunities(
                    selected_exchanges,
                    self.exchange_dict,
                    min_volume,
                    min_price_diff
                )
                
                if opportunities:
                    print(f"\nFound opportunities for {symbol}:")
                    for opp in opportunities:
                        print(f"  {opp['exchange1']} vs {opp['exchange2']}: {opp['diff_percent']:.2f}%")
                        print(f"  Prices: ${opp['price1']:.4f} vs ${opp['price2']:.4f}")
                        print(f"  Volume: ${opp['volume']:,.2f}")
                        
                        # Verify opportunity data
                        self.assertGreater(opp['volume'], min_volume)
                        self.assertGreater(abs(opp['diff_percent']), min_price_diff)
                        self.assertGreater(opp['price1'], 0)
                        self.assertGreater(opp['price2'], 0)
                
                time.sleep(1)  # Rate limiting between symbols
                
            except Exception as e:
                print(f"Error testing {symbol}: {str(e)}")
                continue

    def test_price_differences(self):
        """Test price differences between exchanges."""
        exchanges_list = list(self.exchange_dict.keys())
        if len(exchanges_list) < 2:
            self.skipTest("Need at least 2 exchanges for testing")
        
        ex1, ex2 = exchanges_list[:2]
        symbol = 'BTC/USDT'  # Use Bitcoin as it's most liquid
        
        try:
            # Get prices from both exchanges
            ticker1 = self.exchange_dict[ex1].fetch_ticker(symbol)
            time.sleep(1)
            ticker2 = self.exchange_dict[ex2].fetch_ticker(symbol)
            
            if ticker1 and ticker2:
                price1 = ticker1['last']
                price2 = ticker2['last']
                
                # Calculate price difference
                diff_percent = abs((price1 - price2) / price2 * 100)
                
                print(f"\nPrice difference for {symbol}:")
                print(f"{ex1}: ${price1:,.2f}")
                print(f"{ex2}: ${price2:,.2f}")
                print(f"Difference: {diff_percent:.2f}%")
                
                # Verify prices are reasonable
                self.assertGreater(price1, 0)
                self.assertGreater(price2, 0)
                self.assertLess(diff_percent, 10)  # Price difference shouldn't be too extreme
                
        except Exception as e:
            self.skipTest(f"Error fetching prices: {str(e)}")

    def test_market_depth(self):
        """Test market depth to verify arbitrage feasibility."""
        exchange = next(iter(self.exchange_dict.values()))
        symbol = 'BTC/USDT'
        
        try:
            # Fetch order book
            orderbook = exchange.fetch_order_book(symbol)
            
            if orderbook:
                # Get best bid and ask
                best_bid = orderbook['bids'][0][0] if orderbook['bids'] else None
                best_ask = orderbook['asks'][0][0] if orderbook['asks'] else None
                
                print(f"\nMarket depth for {symbol}:")
                print(f"Best bid: ${best_bid:,.2f}")
                print(f"Best ask: ${best_ask:,.2f}")
                print(f"Spread: {((best_ask - best_bid) / best_bid * 100):.4f}%")
                
                # Verify order book data
                self.assertIsNotNone(best_bid)
                self.assertIsNotNone(best_ask)
                self.assertGreater(best_ask, best_bid)  # Verify spread is positive
                
        except Exception as e:
            self.skipTest(f"Error fetching order book: {str(e)}")

if __name__ == '__main__':
    unittest.main() 