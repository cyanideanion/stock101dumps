import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime as dt
from data_loader import (
    get_spy_data, get_vix_data, get_sh_data,
    get_gv_data, get_options_data
)
import content

# ==========================================
# Page Configuration
# ==========================================
st.markdown("""
    <style>
        .stTabs {
            background-color: #f9f9f9;
            padding: 1rem;
            border-radius: 15px;

        }
        div[data-baseweb="tab-list"] {
            background-color: #eeeeee;
            border-radius: 10px 10px 0 0;
            padding: 5px;
            padding-left: 15px;
            gap: 20px;
        }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Market Sentiment Dashboard", layout="wide")

st.title("U.S. Stock Market Sentiment Dashboard")

# --- Spectrum at Top of Page ---
def sentiment_legend_custom_text():
    bg_red = "#FFE9E9"
    bg_blue = "#E8F2FF"
    bg_green = "#E8F9EE"

    text_color_red = "#BD4043"
    text_color_blue = "#0054A3"
    text_color_green = "#158237"

    st.markdown(
        f"""
        <style>
        .spectrum-container {{
            display: flex;
            width: 100%;
            height: 50px;
            border-radius: 10px;
            overflow: hidden;
            font-family: 'Source Sans Pro', sans-serif;
        }}
        .segment {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: 500;
            text-align: center;
            padding: 2px;
            border-right: 1px solid rgba(255,255,255,0.2);
        }}
        .segment:last-child {{
            border-right: none;
        }}
        </style>

        <div class="spectrum-container">
            <div class="segment" style="background-color: {bg_red}; color: {text_color_red};">
                <span class="label-text">Extreme Fear<br>(0-24)</span>
            </div>
            <div class="segment" style="background-color: {bg_red}; color: {text_color_red};">
                <span class="label-text">Fear<br>(25-44)</span>
            </div>
            <div class="segment" style="background-color: {bg_blue}; color: {text_color_blue};">
                <span class="label-text">Neutral<br>(45-55)</span>
            </div>
            <div class="segment" style="background-color: {bg_green}; color: {text_color_green};">
                <span class="label-text">Greed<br>(56-75)</span>
            </div>
            <div class="segment" style="background-color: {bg_green}; color: {text_color_green};">
                <span class="label-text">Extreme Greed<br>(76-100)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

sentiment_legend_custom_text()

# ==========================================
# Current Aggregate Sentiment Calculation and Plotting
# ==========================================

# Sentiment label functions for individual indicators (also used in tabs)

THRESHOLD_VALUE = ["Extreme Greed","Greed","Neutral","Fear","Extreme Fear"]

overall_threshold = [76,56,45,25]
spy_threshold = [76,56,45,25]
vix_threshold = [95,80,20,5]
sh_threshold = [75,60,40,25]
gv_threshold = [90,70,40,20]

def get_sentiment_label(s, threshold):
    """Categorizes the 0-100 average into a sentiment string."""
    for i in range(4):
        if s >= threshold[i]: return THRESHOLD_VALUE[i]
    return THRESHOLD_VALUE[-1]

def get_overall_sentiment_string(s):
    return get_sentiment_label(s, overall_threshold)

def get_spy_sentiment_string(s):
    return get_sentiment_label(s, spy_threshold)

def get_vix_sentiment_string(s):
    return get_sentiment_label(s, vix_threshold)

def get_sh_sentiment_string(s):
    return get_sentiment_label(s, sh_threshold)

def get_gv_sentiment_string(s):
    return get_sentiment_label(s, gv_threshold)

# --- Data Fetching & Score Calculation ---

# Tab1 Col1. S&P 500 Trend
df_spy = get_spy_data()
if isinstance(df_spy.columns, pd.MultiIndex):
    df_spy.columns = df_spy.columns.get_level_values(0)
df_spy['125MA'] = df_spy['Close'].rolling(window=125).mean()
df_spy['Diff'] = df_spy['Close'] - df_spy['125MA']
df_spy['Score'] = df_spy['Diff'].rolling(window=365).rank(pct=True) * 100
df_spy['Sentiment'] = df_spy['Score'].apply(get_spy_sentiment_string)

# Tab1 Col2. VIX Trend (Inverted)
vix_data = get_vix_data()
if isinstance(vix_data.columns, pd.MultiIndex):
    vix_data.columns = vix_data.columns.get_level_values(0)
vix_df = vix_data[['Close']].copy()
vix_df['50MA'] = vix_df['Close'].rolling(window=50).mean()
vix_df['Diff'] = vix_df['Close'] - vix_df['50MA']
vix_df['Percentile'] = vix_df['Diff'].rolling(window=252).rank(pct=True) * 100
vix_df['Calculated_Score'] = 100 - vix_df['Percentile']
vix_df['Sentiment'] = vix_df['Calculated_Score'].apply(get_vix_sentiment_string)

# Tab2 Col1. Safe Haven Demand
sh_data = get_sh_data()
if isinstance(sh_data.columns, pd.MultiIndex):
    sh_data.columns = sh_data.columns.get_level_values(0)
sh_returns = sh_data.pct_change(20).dropna()
sh_returns['Spread'] = sh_returns['SPY'] - sh_returns['IEF']
sh_returns['Score'] = sh_returns['Spread'].rolling(window=252).rank(pct=True) * 100
sh_returns['Sentiment'] = sh_returns['Score'].apply(get_sh_sentiment_string)

# Tab2 Col2. Growth vs Value
gv_data = get_gv_data()
if isinstance(gv_data.columns, pd.MultiIndex):
    gv_data.columns = gv_data.columns.get_level_values(0)
gv_returns = gv_data.pct_change(periods=252)
gv_dev = pd.DataFrame(index=gv_returns.index)
gv_dev['IVW_dev'] = (gv_returns['IVW'] - gv_returns['SPY']) * 100
gv_dev['IVE_dev'] = (gv_returns['IVE'] - gv_returns['SPY']) * 100
gv_dev['Diff'] = gv_dev['IVW_dev'] - gv_dev['IVE_dev']
gv_dev['Score'] = gv_dev['Diff'].rolling(window=252).rank(pct=True) * 100
gv_dev['Sentiment'] = gv_dev['Score'].apply(get_gv_sentiment_string)

# --- Combine and Average Scores ---
spy_scores = df_spy[['Score']].rename(columns={'Score': 'spy_score'})
vix_scores = vix_df[['Calculated_Score']].rename(columns={'Calculated_Score': 'vix_score'})
sh_scores = sh_returns[['Score']].rename(columns={'Score': 'sh_score'})
gv_scores = gv_dev[['Score']].rename(columns={'Score': 'gv_score'})

combined_sentiment_df = pd.concat([spy_scores, vix_scores, sh_scores, gv_scores], axis=1, join='outer')
# Calculate the simple average across all four indicators
combined_sentiment_df['overall_average_sentiment'] = combined_sentiment_df[['spy_score', 'vix_score', 'sh_score', 'gv_score']].mean(axis=1)
# Categorize based on user-defined ranges
combined_sentiment_df['overall_label'] = combined_sentiment_df['overall_average_sentiment'].apply(get_overall_sentiment_string)

# Get current score
latest_score = combined_sentiment_df['overall_average_sentiment'].iloc[-1]
latest_label = combined_sentiment_df['overall_label'].iloc[-1]

# Display Current Aggregate Sentiment
st.subheader(" ")
st.header("Current Aggregate Sentiment")
col_stat, col_chart = st.columns([1, 3])

with col_stat:
    if latest_label == "Extreme Greed": st.success(f"**{latest_label}**")
    elif latest_label == "Greed": st.success(f"**{latest_label}**")
    elif latest_label == "Neutral": st.info(f"**{latest_label}**")
    elif latest_label == "Fear": st.error(f"**{latest_label}**")
    else: st.error(f"**{latest_label}**")

    st.metric("Aggregate Score", f"{latest_score:.0f}/100")
    #st.write("This score is the simple average of all four market indicators.")

with col_chart:
    # --- Historical Market Sentiment Plot ---
    fig_overall_sentiment = go.Figure()

    fig_overall_sentiment.add_trace(go.Scatter(
        x=combined_sentiment_df.index,
        y=combined_sentiment_df['overall_average_sentiment'],
        mode='lines',
        name='Overall Sentiment',
        customdata=combined_sentiment_df['overall_label'],
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>Score:</b> %{y:.0f}<br><b>Sentiment:</b> %{customdata}<extra></extra>'
    ))

    start_date_plot_os = combined_sentiment_df.index.max() - pd.DateOffset(years=1)
    fig_overall_sentiment.update_layout(
        dragmode='pan',
        title='Historical Market Sentiment',
        xaxis_title='', yaxis_title='Aggregate Sentiment Score',
        hovermode='x unified',
        # Set default X-axis view to the last 1 year
        xaxis_range=[start_date_plot_os, combined_sentiment_df.index.max()],
        # Set Y-range to 0-100
        yaxis_range=[0, 100],
        # Enable interval selector
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            type="date"
        )
    )
    st.plotly_chart(fig_overall_sentiment, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})

# Setup tabs for different catagories of indicators
tab1, tab2, tab3, tab4 = st.tabs(["Market Trend", "Flight-To-Safety", "Research Appendix", "Options Activity"])


# ==========================================
# TAB 1: MARKET Trend
# ==========================================
with tab1:
    # --- Technical Momentum ---

    col1, col2 = st.columns([1, 3])

    # [SentimentScore_SPY125MA.py]

    latest_spy = df_spy.iloc[-1]
    score_spy = latest_spy['Score']

    def get_spy_sentiment(s):
      if s >= 76:
          return st.success(f"**Extreme Greed**")
      elif s >= 56:
          return st.success(f"**Greed**")
      elif s >= 45:
          return st.info(f"**Neutral**")
      elif s >= 25:
          return st.error(f"**Fear**")
      else:
          return st.error(f"**Extreme Fear**")

    # Title, Sentiment, and Description
    with col1:
        st.subheader("Technical Momentum")
        get_spy_sentiment(score_spy)
        #st.metric("Score", f"{score_spy:.0f}/100")
        st.write("Computed based on the percentile deviation of the current SPY price from its 125-day Moving Average. This moving average reflects the ongoing medium-term trading momentum of the S&P 500. Markets trading above their trend tend to reflect confidence and risk-taking behavior. Vice versa, persistent moves below this level often signal growing caution and weakening investor conviction.")

    # [Plotly_SPY125MA.py]

    end_date_plot = df_spy.index.max()
    start_date_plot = end_date_plot - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask = (df_spy.index >= start_date_plot) & (df_spy.index <= end_date_plot)
    recent_data = df_spy.loc[mask]
    y_min = recent_data['Close'].min() * 0.95 # 5% buffer
    y_max = recent_data['Close'].max() * 1.05 # 5% buffer

    # Generate Plotly
    with col2:
        plot_spy = df_spy
        fig_spy = go.Figure()
        fig_spy.add_trace(go.Scatter(x=plot_spy.index, y=plot_spy['Close'], name='SPY',
                                     customdata=plot_spy['Sentiment'],
                                     hovertemplate='<b>Price (SPY):</b> %{y:.2f}<br><b>Sentiment:</b> %{customdata}<extra></extra>'))
        fig_spy.add_trace(go.Scatter(x=plot_spy.index, y=plot_spy['125MA'], name='125MA',
                                     hovertemplate='<b>125MA:</b> %{y:.2f}<extra></extra>'))

        fig_spy.update_layout(
            dragmode='pan',
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            title='SPY vs 125-Day Moving Average',
            yaxis_title='Price',
            hovermode='x unified',
            # Set default X-axis view to the last 1 year
            xaxis_range=[start_date_plot, end_date_plot],
            # Set Y-range based on the 1-year slice calculated above
            yaxis_range=[y_min, y_max],
            # Enable interval selector
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                type="date"
            )
        )
        st.plotly_chart(fig_spy, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})


    # --- Volatilit Shocks ---

    col1, col2 = st.columns([1, 3])

    # [SentimentScore_VIX.py]

    score_vix = 100 - vix_df['Percentile'].iloc[-1]

    def get_vix_sentiment(s):
      if s >= 95:
          return st.success(f"**Extreme Greed**")
      elif s >= 80:
          return st.success(f"**Greed**")
      elif s >= 20:
          return st.info(f"**Neutral**")
      elif s >= 5:
          return st.error(f"**Fear**")
      else:
          return st.error(f"**Extreme Fear**")

    # Title, Sentiment, and Description
    with col1:
        st.subheader("Volatilit Shocks")
        get_vix_sentiment(score_vix)
        #st.metric("Score", f"{score_vix:.0f}/100")
        st.write("Computed based on the percentile deviation of the current VIX from its 50-day Moving Average. The CBOE Volatility Index (VIX) measures the S&P 500’s expected volatility in the next 30 days based on the trading activities of its options. However, looking at the VIX directly dilutes actual sentiments with institutional hedging. Therefore, relativity to its short-term movement helps smooth these noises.")

    # [Plotly_VIX.py]

    # Calculate date ranges for the default 1-year view
    end_date_vix = vix_df.index.max()
    start_date_vix = end_date_vix - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask_vix = (vix_df.index >= start_date_vix) & (vix_df.index <= end_date_vix)
    recent_vix = vix_df.loc[mask_vix]
    vix_y_min = recent_vix['Close'].min() * 0.9 # 10% buffer
    vix_y_max = recent_vix['Close'].max() * 1.1 # 10% buffer

    # Generate Plotly
    with col2:
        fig_vix = go.Figure()
        fig_vix.add_trace(go.Scatter(x=vix_df.index, y=vix_df['Close'], name='VIX',
                                     customdata=vix_df['Sentiment'],
                                     hovertemplate='<b>VIX Close:</b> %{y:.2f}<br><b>Sentiment:</b> %{customdata}<extra></extra>'))
        fig_vix.add_trace(go.Scatter(x=vix_df.index, y=vix_df['50MA'], name='50MA',
                                     hovertemplate='<b>50MA:</b> %{y:.2f}<extra></extra>'))

        fig_vix.update_layout(
            dragmode='pan',
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            title='VIX vs 50-Day Moving Average',
            yaxis_title='Index',
            hovermode='x unified',
            # Set default X-axis view to the last 1 year
            xaxis_range=[start_date_vix, end_date_vix],
            # Set Y-range based on the 1-year slice calculated above
            yaxis_range=[vix_y_min, vix_y_max],
            # Enable interval selector
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                type="date"
            )
        )
        st.plotly_chart(fig_vix, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})


# ==========================================
# TAB 2: Flight-To-Safety
# ==========================================
with tab2:
    # --- Cross-Asset ---

    col1, col2 = st.columns([1, 3])

    # [SentimentScore_SafeHavenDemand.py]

    latest_sh = sh_returns.iloc[-1]
    score_sh = latest_sh['Score']

    def get_sh_sentiment(sentiment):
        if sentiment <= 25:
          return st.error(f"**Extreme Fear**")
        elif sentiment <= 40:
          return st.error(f"**Fear**")
        elif sentiment <= 60:
          return st.info(f"**Neutral**")
        elif sentiment <= 75:
          return st.success(f"**Greed**")
        else:
          return st.success(f"**Extreme Greed**")

    # Title, Sentiment, and Description
    with col1:
        st.subheader("Cross-Asset")
        get_sh_sentiment(score_sh)
        #st.metric("Score", f"{score_sh:.0f}/100")
        st.write("Stocks and bonds historically have an inverse relationship due to risk-related factors that are directly tied to trading sentiments. A preference for stocks typically signals optimism about economic growth and earnings. A shift toward bonds often indicates rising uncertainty or risk aversion. Because capital flows often move ahead of price trends, this spread can reveal sentiment shifts early.")

    # [Plotly_SafeHavenDemand.py]

    # Calculate date ranges for the default 1-year view
    end_date_sh = sh_returns.index.max()
    start_date_sh = end_date_sh - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask_sh = (sh_returns.index >= start_date_sh) & (sh_returns.index <= end_date_sh)
    recent_sh = sh_returns.loc[mask_sh]
    sh_y_min = recent_sh['Spread'].min() * 100 - 0.5 # 0.5% buffer
    sh_y_max = recent_sh['Spread'].max() * 100 + 0.5 # 0.5% buffer

    # Generate Plotly
    with col2:
        fig_sh = go.Figure()
        fig_sh.add_trace(go.Scatter(
            x=sh_returns.index,
            y=sh_returns['Spread'] * 100,
            mode='lines',
            name='SPY-IEF',
            customdata=sh_returns['Sentiment'],
            hovertemplate='<b>Spread:</b> %{y:.2f}%<br><b>Sentiment:</b> %{customdata}<extra></extra>'
        ))

        # Zero Line (Reference) - no sentiment needed here
        fig_sh.add_trace(go.Scatter(
            x=[sh_returns.index.min(), sh_returns.index.max()],
            y=[0, 0],
            mode='lines',
            line=dict(color='red', dash='dash', width=1),
            name='Baseline',
            showlegend=True,
            hovertemplate='<b>Baseline:</b> %{y:.2f}%<extra></extra>'
        ))

        fig_sh.update_layout(
            dragmode='pan',
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            title='20-Day Yield Spread: SPY vs IEF',
            yaxis_title='Difference in 20-Day Yield (%)',
            hovermode='x unified',
            # Set default X-axis view to the last 1 year
            xaxis_range=[start_date_sh, end_date_sh],
            # Set Y-range based on the 1-year slice calculated above
            yaxis_range=[sh_y_min, sh_y_max],
            # Enable interval selector
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                type="date"
            )
        )
        st.plotly_chart(fig_sh, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})


    # --- Sector Rotation ---

    col1, col2 = st.columns([1, 3])

    # [SentimentScore_IVWvsIVE.py]

    latest_gv = gv_dev.iloc[-1]

    def get_gv_sentiment(s):
      if s >= 90:
          return st.success(f"**Extreme Greed**")
      elif s >= 70:
          return st.success(f"**Greed**")
      elif s >= 40:
          return st.info(f"**Neutral**")
      elif s >= 20:
          return st.error(f"**Fear**")
      else:
          return st.error(f"**Extreme Fear**")

    # Title, Sentiment, and Description
    with col1:
        st.subheader("Sector Rotation")
        get_gv_sentiment(latest_gv['Score'])
        #st.metric("Score", f"{latest_gv['Score']:.0f}/100")
        st.write("Sector rotation is very common and a core strategy for institutional traders, involving large capital shifts between market areas to capitalize on changing economic cycles and environment. Favoritism in growth stocks often reflects confidence, liquidity, and tolerance for risk. Value stocks tend to outperform during more cautious or late-cycle environments. ")

    # --- Plotly_IVWvsIVE.py ---

    # Calculate date ranges for the default 1-year view
    end_date_gv = gv_dev.index.max()
    start_date_gv = end_date_gv - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask_gv = (gv_dev.index >= start_date_gv) & (gv_dev.index <= end_date_gv)
    recent_gv = gv_dev.loc[mask_gv]
    gv_y_min = min(recent_gv['IVW_dev'].min(), recent_gv['IVE_dev'].min()) - 2.0  # 2% buffer
    gv_y_max = max(recent_gv['IVW_dev'].max(), recent_gv['IVE_dev'].max()) + 2.0  # 2% buffer

    # Generate Plotly
    with col2:
        fig_gv = go.Figure()
        fig_gv.add_trace(go.Scatter(x=gv_dev.index, y=gv_dev['IVW_dev'], name='IVW',
                                    customdata=gv_dev['Sentiment'],
                                    hovertemplate='<b>IVW Dev:</b> %{y:.2f}%<br><b>Sentiment:</b> %{customdata}<extra></extra>'))
        fig_gv.add_trace(go.Scatter(x=gv_dev.index, y=gv_dev['IVE_dev'], name='IVE',
                                    hovertemplate='<b>IVE Dev:</b> %{y:.2f}%<extra></extra>'))

        fig_gv.update_layout(
            dragmode='pan',
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            title='Growth Stocks vs Value Stocks (Relative to SPY)',
            yaxis_title='Deviation from S&P 500 (%)',
            hovermode='x unified',
            # Set default X-axis view to the last 1 year
            xaxis_range=[start_date_gv, end_date_gv],
            # Set Y-range based on the 1-year slice calculated above
            yaxis_range=[gv_y_min, gv_y_max],
            # Enable interval selector
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                type="date"
            )
        )
        st.plotly_chart(fig_gv, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})


# ==========================================
# TAB 3: RESEARCH APPENDIX
# ==========================================
with tab3:

    st.write("**Methodological Note:** Analyses shown here are descriptive and conditional. They are not presented as trading strategies, and no transaction costs, leverage, or execution assumptions are modeled.")

    #st.divider()

    # --- Correlation Analysis ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Correlation Analysis")
        # Access the text from the dictionary
        texts = content.RESEARCH_APPENDIX["correlation_analysis"]
        st.write(texts["method"])
        st.write(texts["results"])
        st.write(texts["discussion"])

    with col2:
        def analyze_standardized_correlation(combined_sentiment_df, df_spy):
            df = pd.concat([
                combined_sentiment_df[['overall_average_sentiment']],
                df_spy[['Close']]
            ], axis=1).dropna()

            df['sentiment_pct'] = df['overall_average_sentiment'].pct_change()
            df['spy_pct'] = df['Close'].pct_change()
            df.dropna(inplace=True)

            # Z-Score Standardization
            df['sentiment_z'] = (df['sentiment_pct'] - df['sentiment_pct'].mean()) / df['sentiment_pct'].std()
            df['spy_z'] = (df['spy_pct'] - df['spy_pct'].mean()) / df['spy_pct'].std()
            df['rolling_corr'] = df['sentiment_z'].rolling(window=60).corr(df['spy_z'])

            # --- Generate Plot ---
            # Subplot: isolates Z-Score and Correlation Analysis
            fig = make_subplots(
              rows=2, cols=1,
              shared_xaxes=True,
              vertical_spacing=0.1,
              subplot_titles=(
                  f"Z-Scores of Daily % Changes", "60-Day Rolling Correlation of Standardized % Change"
              )
            )

            # Top Plot: Z-Score Comparison
            # Visualizes correlation during extreme scenarios
            fig.add_trace(go.Scatter(
                x=df.index, y=df['spy_z'],
                name="SPY",
                line=dict(color='#1f77b4', width=1),
                opacity=0.5
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df.index, y=df['sentiment_z'],
                name="Sentiment",
                line=dict(color='#bd4043', width=1),
                opacity=0.5
            ), row=1, col=1)

            # Bottom Plot: Rolling Correlation
            fig.add_trace(go.Scatter(
                x=df.index, y=df['rolling_corr'],
                name="60D Roll. Corr.",
                fill='tozeroy',
                line=dict(color='#1f77b4')
            ), row=2, col=1)

            fig.update_layout(
                title_text="Market Sentiment Score vs. SPY Performance",
                yaxis_range=[-3, 3],
                height=750,
                template="plotly_white",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                dragmode='pan',
                paper_bgcolor='#f9f9f9',
                plot_bgcolor='#f9f9f9'
            )

            fig.update_yaxes(title_text="Standard Deviations (Z-Score)", row=1, col=1)
            fig.update_yaxes(title_text="Correlation Coefficient", range=[-1, 1], row=2, col=1)
            return fig

        fig_corr = analyze_standardized_correlation(combined_sentiment_df, df_spy)
        st.plotly_chart(fig_corr, width='stretch')

    st.divider()

    # --- Recorvery Time Analysis ---
    col1, col2 = st.columns([1, 0.5])

    with col1:
        st.subheader("Recorvery Time Analysis")
        # Access the text from the dictionary
        texts = content.RESEARCH_APPENDIX["recovery_analysis"]
        st.write(texts["method"])
        st.write(texts["results"])
        st.write(texts["discussion"])

    with col2:
        def plot_recovery_boxplot(combined_sentiment_df):
            df = combined_sentiment_df[['overall_average_sentiment']].copy()
            df.index = pd.to_datetime(df.index)

            EF_THRESHOLD, NEUTRAL_THRESHOLD = 25, 45 # Sentiment Score Threasholds
            is_extreme_fear = df['overall_average_sentiment'] < EF_THRESHOLD # Triggers counter when score < 25
            ef_entries = df.index[is_extreme_fear & (~is_extreme_fear.shift(1, fill_value=False))]

            durations = []
            for start_date in ef_entries:
                future_data = df.loc[start_date:]
                recovery_event = future_data[future_data['overall_average_sentiment'] >= NEUTRAL_THRESHOLD] # Count calendar days until score >= 45
                if not recovery_event.empty:
                    durations.append((recovery_event.index[0] - start_date).days)

            if not durations:
                return None

            # --- Generate Plot ---
            fig = go.Figure(go.Box(
                y = durations,
                name = "Days",
                boxpoints = 'all', # Show all underlying data points next to the box
                jitter = 0.5,      # Spread out points so they don't overlap
                pointpos = -1.8,   # Position of points relative to the box
                line = dict(color='#1f77b4'),
                hovertemplate = 'Days: %{y}<extra></extra>'
            ))

            # Update Layout to match Dashboard theme
            fig.update_layout(
                title={
                    'text': "Distribution of Recovery Times: Extreme Fear to Neutral",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                yaxis_title="Calendar Days until Recovery",
                xaxis=dict(showticklabels=False),
                template="plotly_white",
                #width=1200,
                height=800,
                showlegend=False,
                dragmode='pan',
                paper_bgcolor='#f9f9f9',
                plot_bgcolor='#f9f9f9'
            )
            return fig

        fig_recov = plot_recovery_boxplot(combined_sentiment_df)
        st.plotly_chart(fig_recov, width='stretch')

    st.divider()

    # --- Forward Performance Analysis ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Forward Performance Analysis")
        # Access the text from the dictionary
        texts = content.RESEARCH_APPENDIX["forward_performance"]
        st.write(texts["method"])
        st.write(texts["results"])
        st.write(texts["discussion"])

    with col2:
        def plot_multi_horizon_performance(combined_sentiment_df, df_spy):

            data = pd.DataFrame(index=combined_sentiment_df.index)
            data['Label'] = combined_sentiment_df['overall_label']
            data['Price'] = df_spy['Close']
            data.dropna(subset=['Label', 'Price'], inplace=True)

            horizons = {'6-Month': 126, '12-Months': 252, '24-Months': 504, '36-Months': 756} # Trading day approximations

            for name, period in horizons.items():
                data[f'{name}_Ret'] = (data['Price'].shift(-period) / data['Price'] - 1) * 100

            label_order = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
            performance_cols = [f'{name}_Ret' for name in horizons.keys()]

            long_df = data.melt(id_vars=['Label'], value_vars=performance_cols, var_name='Horizon_Ret_Col', value_name='Return')
            long_df['Horizon'] = long_df['Horizon_Ret_Col'].str.replace('_Ret', '')
            long_df['Label'] = pd.Categorical(long_df['Label'], categories=label_order, ordered=True)
            long_df.sort_values(by=['Label', 'Horizon'], inplace=True)

            fig = go.Figure()
            colors = ['#aec7e8', '#7fb3d5', '#2980b9', '#154360'] # Light to Dark Blue

            for i, horizon_name in enumerate(horizons.keys()):
                horizon_data = long_df[long_df['Horizon'] == horizon_name]
                fig.add_trace(go.Box(
                    x=horizon_data['Label'],
                    y=horizon_data['Return'],
                    name=horizon_name,
                    marker_color=colors[i],
                    boxpoints='outliers',
                    boxmean=True))

            fig.update_layout(
                  title={
                      'text': "Distribution of Forward Returns by Aggregate Sentiment Regime",
                      'y': 0.95, 'x': 0.5, 'xanchor': 'center'
                  },
                  xaxis_title="Aggregate Sentiment",
                  yaxis_title="Forward Return (%)",
                  boxmode='group', # Groups the boxes for each sentiment label
                  template="plotly_white",
                  legend=dict(
                      orientation="h",
                      yanchor="bottom", y=1.02,
                      xanchor="right", x=1
                  ),
                  height=600,
                  dragmode='pan',
                  paper_bgcolor='#f9f9f9',
                  plot_bgcolor='#f9f9f9'
              )

            fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
            return fig

        fig_perf = plot_multi_horizon_performance(combined_sentiment_df, df_spy)
        st.plotly_chart(fig_perf, width='stretch')


# ==========================================
# TAB 4: OPTIONS ACTIVITY
# ==========================================
with tab4:
    # --- Put/Call Sentiment ---

    col1, col2 = st.columns([1, 3])

    option_chains, current_price = get_options_data('SPY')

    # [SentimentScore_PutCall_Ratio.py]

    pcr_results = []

    for entry in option_chains:
      date = entry['date']
      calls = entry['calls']
      puts = entry['puts']

      # Access volume and openInterest directly from the calls and puts DataFrames
      v_put = puts['volume'].sum()
      v_call = calls['volume'].sum()
      oi_put = puts['openInterest'].sum() # Corrected access
      oi_call = calls['openInterest'].sum() # Corrected access

      # Calculate ratios with safety checks for division by zero
      v_ratio = v_put / v_call if v_call > 0 else 0
      oi_ratio = oi_put / oi_call if oi_call > 0 else 0

      pcr_results.append({'date': date, 'v_pcr': v_ratio, 'oi_pcr': oi_ratio})

    pcr_df = pd.DataFrame(pcr_results)
    # Simple logic for "Highest Sentiment" quadrant
    avg_v = pcr_df['v_pcr'].mean()
    avg_oi = pcr_df['oi_pcr'].mean()

    def get_pcr_sentiment(s):
      sentiment_label = "Neutral"
      if avg_v > 1.0 and avg_oi > 1.0:
        return st.error(f"**Capitulation**")
      elif avg_v < 1.0 and avg_oi < 1.0:
        return st.success(f"**Bullish Setup**")
      elif avg_v > 1.0 and avg_oi < 1.0:
        return st.info(f"**Tactical Hedging**")
      elif avg_v < 1.0 and avg_oi > 1.0:
        return st.info(f"**Short Covering**")

    # Title, Sentiment, PCR, and Description
    with col1:
        st.subheader("Put/Call Sentiment")
        get_pcr_sentiment(pcr_df)
        st.write("Avg Vol PCR:", f"{avg_v:.2f}")
        st.write("Avg OI PCR:", f"{avg_oi:.2f}")
        st.write("Put/Call Ratio measures the trading activity on Put relative to Call options. A ratio above 1 suggests bearish sentiment (more puts), while below 1 indicates bullishness (more calls). Furthermore, PCR can be divided into volume and open interest, which can be roughly interpreted as the immediate flow and existing commitment, respectively.")

    # [Plotly_PutCall_Ratio.py]

    today_ts = pd.Timestamp(dt.now().date())
    pcr_df['DTE'] = (pd.to_datetime(pcr_df['date']) - today_ts).dt.days

    with col2:
        fig_pcr = go.Figure(data=[
            go.Bar(x=pcr_df['DTE'], y=pcr_df['v_pcr'], name='Vol',
              hovertemplate='<b>DTE:</b> %{x}<br><b>Volume PCR:</b> %{y:.2f}<extra></extra>'),
            go.Bar(x=pcr_df['DTE'], y=pcr_df['oi_pcr'], name='OI',
              hovertemplate='<b>DTE:</b> %{x}<br><b>OI PCR:</b> %{y:.2f}<extra></extra>')
        ])
        fig_pcr.update_layout(
            dragmode='pan',
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            title='Put/Call Ratios (Nearest 14 Expirations)',
            xaxis=dict(
                title='DTE',
                type='category',
                tickvals=pcr_df.index,
                ticktext=pcr_df['DTE']
                )
            )
        st.plotly_chart(fig_pcr, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})


    # --- Skew Diagnostics ---
    col1, col2 = st.columns([1, 3])

    # [SentimentScore_VolatilitySkew.py]
    ATM_WIN, OTM_PCT = 0.01, 0.10 # 1% ATM window, +-10% OTM window
    skew_results = []

    # Plotly_VolatilitySkew.py moved ahead to share option_chains loop
    # Color code calls and puts, lighter color = further expiration
    fig_skew = go.Figure()

    # Set default X-axis view to +-5% from current SPY price
    x_min, x_max = current_price * 0.95, current_price * 1.05
    all_ivs = []

    # Per-date loop for the all SPY options in the nearest 14 expirations
    for i, entry in enumerate(option_chains):
        exp_date = entry['date']
        calls = entry['calls'].copy()
        puts = entry['puts'].copy()
        dte = (dt.strptime(exp_date, '%Y-%m-%d').date() - dt.now().date()).days

        calls["type"] = "call"
        puts["type"] = "put"

        # Indentify ATM and OTM options
        df_skew = pd.concat([calls, puts])
        df_skew = df_skew[df_skew["impliedVolatility"] > 0]
        df_skew["moneyness"] = df_skew["strike"] / current_price

        atm = df_skew[(df_skew["moneyness"] > 1 - ATM_WIN) & (df_skew["moneyness"] < 1 + ATM_WIN)]
        otm_calls = df_skew[(df_skew["type"] == "call") & (df_skew["moneyness"] > 1 + OTM_PCT)]
        otm_puts = df_skew[(df_skew["type"] == "put") & (df_skew["moneyness"] < 1 - OTM_PCT)]

        # Compute "Tail-skew", "Put Convexity", and "Call-FOMO"
        if not (atm.empty or otm_calls.empty or otm_puts.empty):
            m = {"tail": otm_puts["impliedVolatility"].mean() / otm_calls["impliedVolatility"].mean(),
                 "put_conv": otm_puts["impliedVolatility"].mean() / atm["impliedVolatility"].mean(),
                 "call_fomo": otm_calls["impliedVolatility"].mean() / atm["impliedVolatility"].mean()}
            skew_results.append(m)

        # Plotly metrics
        for df_opt, color_base in [(calls, '0, 128, 0'), (puts, '255, 0, 0')]:
            df_opt = df_opt[df_opt['impliedVolatility'] > 0.001]
            df_opt['smooth'] = df_opt['impliedVolatility'].rolling(window=5, min_periods=1, center=True).mean()
            alpha = 1.0 - (i / len(option_chains)) * 0.9

            fig_skew.add_trace(
                go.Scatter(
                    x=df_opt['strike'],
                    y=df_opt['smooth'] * 100,
                    mode='lines',
                    line=dict(color=f'rgba({color_base}, {alpha})', width=1),
                    showlegend=False,
                    hovertemplate=(
                        f'<b>DTE:</b> {dte}<br>'
                        '<b>Strike:</b> %{x:.0f}<br>'
                        '<b>IV:</b> %{y:.2f}%'
                        '<extra></extra>'
                        )
                    )
                )
            # Collect IV for axis scaling
            mask = (df_opt['strike'] >= x_min) & (df_opt['strike'] <= x_max)
            all_ivs.extend((df_opt.loc[mask, 'smooth'] * 100).tolist())

    # Diagnostic results based on average
    with col1:
        # Compute the average of "Tail-skew", "Put Convexity", and "Call-FOMO" across all expirations
        df_m = pd.DataFrame(skew_results)
        avg_tail, avg_conv, avg_fomo = df_m["tail"].mean(), df_m["put_conv"].mean(), df_m["call_fomo"].mean()
        ts_slope = df_m.iloc[-1]["tail"] - df_m.iloc[0]["tail"]

        st.subheader("Skew Diagnostics")
        if avg_tail > 1.3: st.error("- Strong downside tail fear")
        elif avg_tail > 1.1: st.warning("- Moderate downside risk awareness")
        else: st.success("- Balanced tail risk")

        if avg_conv > 1.4: st.error("- Crash protection demand elevated")
        if avg_fomo > 1.2: st.warning("- Upside FOMO / squeeze risk")
        if ts_slope < -0.1: st.error("- Near-term fear dominant")
        if ts_slope > 0.2: st.warning("- Long-term risk feared")
        else: st.success("- Stable term-structure sentiment")
        st.write("Implied Volatility (IV) significantly impacts option premiums. IV positively correlates to the expectation that the underlying option ends up “in the money”. Therefore, the volatility skew curve is a direct visualization of supply and demand dynamics influenced by trader sentiments. ")

    # [Plotly_VolatilitySkew.py]

    with col2:
        # Set default Y-axis view to +-5% from ATM IV
        if all_ivs:
            ymin, ymax = min(all_ivs) * 0.95, max(all_ivs) * 1.05
        else:
            ymin, ymax = 0, 100

        # Center line for current SPY price
        fig_skew.add_vline(x=current_price, line_dash="dash", line_color="grey")
        fig_skew.update_layout(
            title=f"Volatility Skew (Current Price: {current_price:.2f})",
            xaxis_title="Strikes",
            yaxis_title="Implied Volatility (IV)",
            xaxis_range=[x_min, x_max],
            yaxis_range=[ymin, ymax],
            height=600,
            dragmode='pan',
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            )
        st.plotly_chart(fig_skew, width='stretch', config={'displayModeBar': False})


