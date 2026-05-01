---
aliases:
created: 2025-10-26T23:07:01-07:00
updated: 2025-11-14T06:29:46-08:00
tags:
  - math
  - math/calculus
  - physics
citations: https://www.youtube.com/watch?v=P2HZelQm7Lw&t=1036s
---
## Summary
The Legendre Transforms allows for a function to be expressed in terms of rates, rather than levels. For example, you can express a function in terms of its slope, rather than its coordinates. It can only be applied to monotonic functions.
## Significance
This can be useful when you are trying to define a function with respect to its own rate of change, rather than coordinates.
## Definition
Given a function $f(x)$, we can find the derivative, $p(x)$. We can then rewrite the derivative function such that the derivative is a function of the coordinate. Thus, $x(p)$.
We now define another function that gives the y-intercept as a function of the derivative. Let $g$ be the y-intercept, we get
$$
\frac{f+g}{x}=p \Rightarrow g=px-f
$$
We thus find the Legendre Transform:
$$g(p)=px(p)-f(x(p))$$
## Reference
- [[Solving for the inverse derivative of a function]]