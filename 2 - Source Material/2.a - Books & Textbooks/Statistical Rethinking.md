---
aliases:
author:
  - "Richard McElreath\r"
created: 2026-06-07T16:39:25-07:00
updated: 2026-06-09T07:35:34-07:00
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
### Chapter 2
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
**2M3**
$$
P(L|E)= \frac{P(E,L)}{P(E)} = P(L|E)= \frac{P(E,L)}{0.5}
$$
$$
P(L|E)= \frac{P(E|L)P(L)}{0.5} = P(L|E)= \frac{0.23(0.5\times 0.3 + 0.5)}{0.5}
$$
$$
0.7= \frac{0.23(0.5\times 0.3 + 0.5)}{0.5}
\square
$$
### Chapter 3
# 3M1
**3M1**
```R
p_grid <- seq(0, 1, length.out=100)
prior <- rep(1, 100)
likelihood <- dbinom(8, 15, prob=p_grid)
posterior <- (likelihood * prior)/(sum(likelihood * prior))
df <- data.frame(p_grid, posterior)

ggplot(df, aes(p_grid, posterior)) +
  geom_line() +
  theme_bw()
```
**3M2**
```R
samples_p <- sample(p_grid, prob=posterior, 10000, replace=TRUE)
hist(samples_p)
HPDI(samples_p, 0.9)
```
**3M3**
```R
posterior_pred <- rbinom(10000, 15, prob=samples_p)
hist(posterior_pred)
probability <- length(posterior_pred[posterior_pred==8])/length(posterior_pred)
```
**3M4**
```R
posterior_pred1 <- rbinom(10000, 9, prob=samples_p)
hist(posterior_pred)
probability1 <- length(posterior_pred[posterior_pred==6])/length(posterior_pred)
```
**3M5**
```R
p_grid <- seq(0, 1, length.out=100)
prior <- ifelse(p_grid>0.5, 1, 0)
likelihood <- dbinom(8, 15, prob=p_grid)
posterior <- (likelihood * prior)/(sum(likelihood * prior))
df <- data.frame(p_grid, posterior)

ggplot(df, aes(p_grid, posterior)) +
  geom_line() +
  theme_bw()
```
## References