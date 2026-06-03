---
aliases:
created: 2025-11-11T16:55:50-08:00
updated: 2026-06-03T12:06:53-07:00
tags:
  - ai
  - ai/llm
  - data
citations: https://www.youtube.com/watch?v=7xTGNNLPyMI&list=WL&index=6&t=4865s
---
## Summary
When a token undergoes inference, there is a limited amount of compute that can be applied to each input token. 
## Significance
This means that reasoning should be spread across various tokens (and thus compute) in order to generate the best response.
## Explanation
For example, asking an LLM to generate the response to a math question and asking it to do by only providing the answer and not the steps crams all of the calculations into one token, thus lowering the potential quality of the response.
## Reference
- [[LLM hallucinations are 'shameless guesses,' not 'hallucinations']]
	- When LLMs make mistakes due to the fact that they were provided too little tokens for a response, this could be the justification.
- [[Reasoning LLMs use reinforcement learning, whereas most models use STF]]
	- Reasoning LLMs could operate in a different manner, where this is less of a problem?