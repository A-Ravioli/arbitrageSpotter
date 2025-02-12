import plotly.graph_objects as go
import streamlit as st
from . import data
import time

def plot_multi_exchange_comparison(symbol, exchanges, exchange_dict):
    """Create and display a price comparison plot across multiple exchanges."""
    fig = go.Figure()
    
    # Color palette for different exchanges
    colors = ['#2962FF', '#26A69A', '#B71C1C', '#00BCD4', '#6200EA', '#FFB300']
    
    for i, exchange_id in enumerate(exchanges):
        exchange = exchange_dict[exchange_id]
        df = data.fetch_ohlcv(exchange, symbol)
        
        if df is not None and not df.empty:
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['close'],
                name=f"{exchange_id.title()}",
                line=dict(color=colors[i % len(colors)]),
                hovertemplate="%{y:$.4f}<extra></extra>"
            ))
    
    # Update layout for dark theme
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='#131722',
        paper_bgcolor='#131722',
        title=dict(
            text=f"{symbol} Price Comparison",
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="Time",
            gridcolor='#1e222d',
            zerolinecolor='#1e222d'
        ),
        yaxis=dict(
            title="Price (USD)",
            gridcolor='#1e222d',
            zerolinecolor='#1e222d',
            tickformat='$,.4f'
        ),
        height=600,
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(30,34,45,0.7)'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_opportunity(opp):
    """Display a single arbitrage opportunity."""
    color = "green" if opp['diff_percent'] > 0 else "red"
    st.markdown(f"""
        <div style='padding: 10px; background-color: #1e222d; border-radius: 4px; margin: 5px 0; border: 1px solid #2a2e39;'>
            <div style='display: flex; justify-content: space-between;'>
                <h4>{opp['symbol']}</h4>
                <span style='color: {color};'>{opp['diff_percent']:.2f}%</span>
            </div>
            <p>{opp['exchange1'].title()} vs {opp['exchange2'].title()}</p>
            <div style='display: flex; justify-content: space-between;'>
                <span>${opp['price1']:,.2f}</span>
                <span>${opp['price2']:,.2f}</span>
            </div>
            <p style='color: #848e9c;'>Volume: ${opp['volume']:,.2f}</p>
        </div>
    """, unsafe_allow_html=True) 