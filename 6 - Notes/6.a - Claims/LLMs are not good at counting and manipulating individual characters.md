---
aliases:
created: 2025-11-10T16:27:44-08:00
updated: 2026-06-03T12:05:24-07:00
tags:
  - ai
  - ai/llm
citations: https://www.youtube.com/watch?v=7xTGNNLPyMI&list=WL&index=4&t=4865s
---
## Summary
Due to the tokenization mechanism behind LLMs, they are not able to complexly manipulate individual characters in strings of text, nor are they good at counting.
## Significance
This explains why although LLMs are often able to answer high level problems, they often struggle with simple operations such as counting or spelling.
## Explanation
Due the nature of tokenization, where words/strings of characters are often represented as one token (so individual manipulation of characters is difficult for the LLM to understand), it is difficult for the model to be able to count or spell well.
## Reference
- [[LLM hallucinations are 'shameless guesses,' not 'hallucinations']]
	- So the result of tasks involving those described in this note can be categorized as such.