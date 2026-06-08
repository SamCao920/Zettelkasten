---
aliases:
author:
  - "Richard McElreath\r"
created: 2026-06-07T16:39:25-07:00
updated: 2026-06-08T09:43:07-07:00
tags:
  - math
  - math/statistics/Bayesian
citations:
  - "[[Statistical Rethinking 2nd Edition.pdf]]"
done:
---
## Summary
A Bayesian statistics textbook that emphasizes intuitive thinking about inference, causality, and model building rather than rote formula manipulation. It teaches how to express scientific questions as probabilistic models, use priors and posterior updating, compare models with information criteria, and reason about uncertainty in a principled way. The book is especially well known for its clear examples, graphics, and use of practical computation in `R` and `Stan`, making advanced statistical ideas accessible to researchers across the natural and social sciences.
## Significance
That textbook teachers Bayesian statistics, something that I am interested in.
## Practice
### 2.6
**2E4**: It would mean that from the point of the person making the statement, based on the knowledge that they have (which may be and is likely at least somewhat inaccurate), they think that the probability that there is water on a random location on an Earth globe has water.
**2M1**
```r
library(tidyverse)

globe <- function(detail, size, successes) {
  p_grid <- seq(0, 1, length.out=detail)
  prior <- rep(1, times=length(p_grid))
  likelihood <- dbinom(successes, size, p_grid)
  unstd_posterior <- likelihood * prior
  posterior <- unstd_posterior/(sum(unstd_posterior))
  
  ggplot(data.frame(posterior, p_grid), aes(p_grid, posterior)) + 
    geom_line() +
    theme_bw()
}

# (1)
globe(200, 3, 3)

# (2) WWWL
globe(200, 4, 3)

# (3) LWWLWWW
globe(1000, 7, 5)
```
## References