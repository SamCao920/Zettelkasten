---
aliases:
created: 2025-09-28T08:48:38-07:00
updated: 2026-02-27T20:36:09-08:00
tags:
  - ai
  - math
  - math
citations: https://youtu.be/GkiITbgu0V0?si=F-aDxeQcf3-TkjLL
feature: 0 - Assets/0.e - In-text Images/Pasted image 20250928085616.png
thumbnail: thumbnails/resized/514c8e12933d72657aee6441640b5ccd_86cf658e.webp
---
## Summary
Gradient descent is the process by which a local minima for a loss function is found (the loss, or inaccuracy, is minimized), thereby producing accurate outputs. 
## Significance
This is used in training AI models to give accurate results.
## Explanation
![[Pasted image 20250928085616.png|Figure 1. Gradient descent finding the approximate minima of a loss function]]
Gradient descent take the form of the following function:
$$
P_{new}(LR) =P_{old} - LR \cdot \frac{\partial L}{\partial P}
$$
This function incrementally adjusts the values of the parameters as to minimize the loss function. Since the gradient descent function is a function of the learning rate ($LR$), by changing the learning rate, the speed at which the minima in the loss function is reached varies accordingly.
A standard derivative cannot be directly used to find the minima, since usually, these functions are in such high dimensions that it would not be as computationally as effective as using gradient descent.
![[Gradient_Descent_in_2D.webm|Figure 2. Gradient descent in action]]

## References
- [[The first derivative test allows for the classification of critical points]]