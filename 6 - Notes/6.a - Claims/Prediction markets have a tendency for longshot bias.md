---
aliases:
created: 2026-01-31T08:53:20-08:00
updated: 2026-01-31T09:18:58-08:00
tags:
  - economics
  - economics
  - economics
citations:
  - https://www.jbecker.dev/research/prediction-market-microstructure
feature: 0 - Assets/0.e - In-text Images/Pasted image 20260131091754.png
thumbnail: thumbnails/resized/7565bae548de93dee099ec4fe98998d4_86cf658e.webp
---
## Summary
Prediction markets have a tendency, especially in high-engagement categories like sports and entertainment, to overestimate the odds of low probability events.
## Significance
This acts as a counter against the existence of an efficient market in predicts markets, and a highlights a potential opportunity for arbitrage.
## Explanation
- All contracts priced below 20 cents underperform their odds, while those above 80 outperform.
- This phenomenon is most observable in specific categories:

| Category      | Taker Return | Maker Return | Gap     | N trades |
| ------------- | ------------ | ------------ | ------- | -------- |
| World Events  | -3.66%       | +3.66%       | 7.32 pp | 0.2M     |
| Media         | -3.64%       | +3.64%       | 7.28 pp | 0.6M     |
| Entertainment | -2.40%       | +2.40%       | 4.79 pp | 1.5M     |
| Crypto        | -1.34%       | +1.34%       | 2.69 pp | 6.7M     |
| Weather       | -1.29%       | +1.29%       | 2.57 pp | 4.4M     |
| Sports        | -1.11%       | +1.12%       | 2.23 pp | 43.6M    |
| Politics      | -0.51%       | +0.51%       | 1.02 pp | 4.9M     |
| Finance       | -0.08%       | +0.08%       | 0.17 pp | 4.4M     |
- There is a consistent advantage for NO contracts by makers (people who set limit deals and provide liquidity for the market).

> [!NOTE] NO contracts are better than YES contracts
> Despite the market being zero-sum, dollar-weighted returns are -1.02% for YES buyers compared to +0.83% for NO buyers, a 1.85 percentage point gap driven by the overpricing of YES contracts.

![[Pasted image 20260131091754.png]]
## References
- [[The Efficient Market Hypothesis cannot account for market anomalies]]
	- This note describes something that the EMH cannot account for, even outside of market anomalies.