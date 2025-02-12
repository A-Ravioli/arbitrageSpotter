# Crypto Arbitrage Spotter

A real-time cryptocurrency arbitrage opportunity finder built with Streamlit and CCXT. This application monitors multiple cryptocurrency exchanges and identifies price differences that could potentially be used for arbitrage trading.

## Features

- Real-time price monitoring across multiple exchanges
- Interactive price comparison charts
- Customizable minimum volume and price difference thresholds
- Auto-refreshing data (can be toggled)
- Manual refresh button
- Support for major exchanges:
  - Bybit
  - MEXC
  - Gate.io
  - Huobi
  - OKX
  - Phemex

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/arbitrageSpotter.git
cd arbitrageSpotter
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Use the sidebar to:
   - Select which exchanges to monitor (minimum 2)
   - Set minimum 24h volume threshold
   - Set minimum price difference threshold
   - Toggle auto-refresh

4. The main interface shows:
   - Price comparison charts for selected pairs
   - Live arbitrage opportunities sorted by percentage difference
   - Last update time
   - Manual refresh button

## Notes

- The app uses rate limiting to respect exchange API limits
- All prices are in USD
- Volume thresholds help filter out low-liquidity opportunities
- The interface auto-refreshes every 30 seconds (can be disabled)
- No API keys required - uses public endpoints only

## Disclaimer

This tool is for educational purposes only. Cryptocurrency arbitrage trading involves various risks including but not limited to:
- Exchange fees
- Transfer times
- Market slippage
- Withdrawal/deposit fees
- Exchange-specific restrictions
- Market liquidity
- Price volatility

Always do your own research and consider all costs before attempting any trading strategy. 