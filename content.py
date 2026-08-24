# research_content.py

RESEARCH_APPENDIX = {
    "correlation_analysis": {
        "method": """
            **Method:** The analysis observes the 60-day rolling correlation of the standardized daily percentage changes (Z-scores) for both the Market Sentiment Score and SPY. 
            By using Z-scores, the data is normalized to a mean of 0 and a standard deviation of 1, 
            allowing for a direct comparison of volatility and movement despite the different original scales of the two metrics.
        """,
        "results": """
            **Results:** 
            \n- **Positive Relationship:** The correlation coefficient consistently remains in positive territory, generally fluctuating between 0.4 and 0.9.
            \n- **Stability:** For the majority of the period from 2017 to 2026, the correlation is robust, frequently hovering near the 0.7 to 0.9 range.
            \n- **Significant Deviations:** Notable “dips” in correlation occurred in early 2020 and early 2025, where the coefficient briefly dropped toward 0.4 to 0.55.
        """,
        "discussion": """
        **Discussion:** The high rolling correlation suggests that the Market Sentiment Score is a strong co-movement indicator for SPY. 
        When sentiment shifts significantly (as seen in the red spikes/dips in the top pane), the SPY (blue lines) tends to follow suit in the same direction. 
        \n However, the periodic sharp drops in the correlation coefficient should be critically examined. 
        These "decoupling" events indicate periods where the Sentiment Score does not accurately reflect the magnitude of movements in the actual stock market, 
        found in timeframes of exogenous shocks (COVID-19) or specific technical trading patterns (TACO trade) where price determination is driven by factors 
        beyond market trend and asset allocation displayed in the previous tabs. 
        """
    },
    "recovery_analysis": {
        "method": """
            **Method:** The analysis utilizes a combination of a scatter plot and a box plot to visualize the distribution of calendar days 
            between the first occurrence of an “Extreme Fear” aggregate sentiment to recovering to a “Neutral” sentiment." 
            The scatter plot shows individual data points to highlight density and outliers, while the box plot provides a statistical summary of the central tendency and spread.
        """,
        "results": """
            **Results:** \n- **Average Recovery Time:** The median time between an “Extreme Fear” occurring to the first “Neutral” after that “Extreme Fear” is 24 days (the horizontal line within the box). 
            \n- **Interquartile Range (IQR):** The middle 50% of recovery events occur between 13 and 37 days. 
            \n- **Full Range:** Recovery times vary significantly, ranging from near-instantaneous (approximately 1 day) to a maximum of 99 days (as seen in the highest outlier). 
            \n- **Typical Outliers:** While most recoveries happen within 40 days, there is a visible cluster of events taking between 40 and 80 days.
        """,
        "discussion": """
            **Discussion:** The Sentiment Score is a function of cross-asset correlation. Time required for arbitrage and rebalancing to occur across these sectors should be considered while examining the recovery distribution. For instance: 
            \n- **VIX Mean Reversion:** Implied volatility spikes and decays in a square-root process, meaning fearful sentiment reflected through option activities typically follow a speedy recovery. 
            \n- **Bonds-Stocks Spread Normalization:** Shift in interest rate expectations or inflationary outlooks that are influenced by monthly macroeconomic data releases, explaining the 20–30 day clustering. 
            \n- **Style Rotation Frictions:** Investor favoritism towards growth versus value companies relates closely to macroeconomic conditions (e.g. discount rate). A recovery to "Neutral" implies that the market has reached a new consensus on the cost of capital, which does have a strict timeframe pattern.
        """
    },
    "forward_performance": {
        "method": """
        **Method:** This analysis observes the distribution of forward returns of the stock market categorized by the five sentiment regimes: 
        Extreme Fear, Fear, Neutral, Greed, and Extreme Greed, across the time horizons of 6, 12, 24, and 36 months through a comparative box plot with outliers in scatter points.
        """,
        "results": """
            **Results:** \n- **Time Consistency:** Forward horizon duration is the primary driver of total returns across all regimes. The 36-month horizon (dark navy) 
            consistently achieves the highest median return (~45%–50%) regardless of initial market sentiment.
            \n- **Stability at Extreme Greed:** Forward return distributions in the “Extreme Greed” regime exhibit low overall variance, 
            a relatively tightly constrained Interquartile Range (IQR), and absence of extreme outliers across all time horizons. 
            \n- **Extreme Fear Leptokurtosis:** Unlike all other sentiment regimes, whose IQRs and central variances expand significantly as time horizons lengthen, 
            ”Extreme Fear” maintains a relatively tighter IQR and variance growth within its middle 50% of outcomes. Converse to “Extreme Greed”, however, 
            “Extreme Fear” simultaneously produces dense clusters of severe downside outliers at short horizons (6–12 months) and massive upside outlier clusters at longer horizons (24–36 months), 
            suggesting persistent fat tails across every observed time frame.
        """,
        "discussion": """
            **Discussion:** Analyzing forward return distributions across aggregate sentiment regimes reveals how prevailing market conditions fundamentally alter volatility, 
            distributional skew, and multi-year compounding mechanics. While longer holding horizons dictate total return magnitude, 
            the initial sentiment regime governs whether those returns accrue through steady fundamental growth or extreme, policy-dependent tail
            \n **Extreme Greed: Structural Multiple Exhaustion:**
            \n- **“Good News is Priced In”:** Long-term (>12 months) forward returns cannot benefit from further multiple expansion or capital reallocation 
            due to growth style rotation and equity risk premiums relative to Treasuries are already maxed out, thus constrained by fundamental earnings growth.
            \n- **Stability & Thin Tails:** Suppression of VIX during “Extreme Greed” regimes reflects heavy options-selling and volatility-harvesting activity, 
            thus creating a noticeably lower downside risk, short-term return stability (tight 6-month IQRs) relative to other regimes. 
            \n **Extreme Fear: Triple Mean-Reversion & Leptokurtic Mechanics:** 
            \n- **“Bad News is Priced In”:** Contrary to “Extreme Greed”, equity valuation multiples and equity prices relative to safer assets have collapsed to near- 
            or below fundamental values, establishing a rigid "margin of safety." For the middle 50% of outcomes, 
            baseline returns are securely backed by fundamental growth and valuation restoration to long-term fair value.
            \n- **Persistent Bidirectional Fat Tails:** “Extreme Fear” is a state of severe structural instability where market outcomes diverge into extreme paths rather than safely converging over time. 
            If the shock represents a cyclical liquidity freeze, government intervention (SPY vs. IEF) and factor mean-reversion (IVW vs. IVE) ignite massive, speedy recoveries. 
            Conversely, structural insolvency (economic crises), secular bear markets, or liquidity traps from policy failure may result in multi-year performance drag.
        """,
    }

}
