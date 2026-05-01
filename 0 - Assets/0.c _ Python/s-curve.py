[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20originate%20in%20the%20agent,%20a%20persisting%20entity%20and%20not%20an%20event.md)[](Free%20actions%20originate%20in%20the%20agent,%20a%20persisting%20entity%20and%20not%20an%20event.md)# S-curve adoption visualization for General-Purpose Technologies (GPTs)
# - Middle label moved left (to avoid overlap)
# - Font set to Times New Roman (with fallbacks)
# - X-axis numbers removed

import numpy as np
import matplotlib.pyplot as plt

# Use Times New Roman if available; sensible fallbacks otherwise
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"]
})

# Logistic (S-curve) parameters
L = 1.0      # Saturation level (1.0 -> 100%)
k = 1.0      # Speed/steepness of adoption
t0 = 5.0     # Inflection point (adoption ~50%)

# Time axis
t = np.linspace(0, 10, 600)

# Logistic adoption curve
adoption = L / (1 + np.exp(-k * (t - t0)))

# Create the plot
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(t, adoption * 100, linewidth=2)

# Titles and labels
ax.set_title("S-Curve Adoption of General-Purpose Technologies (GPTs)")
ax.set_xlabel("Time")
ax.set_ylabel("Cumulative Adoption (%)")

# Grid
ax.grid(True, linestyle="--", alpha=0.5)

# Early slow adoption
ax.annotate(
    "Early slow adoption:\n• Firms reluctant to upend existing processes\n• Contractual & organizational frictions\n• Capabilities still maturing",
    xy=(1.5, (L / (1 + np.exp(-k * (1.5 - t0)))) * 100),
    xytext=(0.5, 35),
    arrowprops=dict(arrowstyle="->"),
    fontsize=9,
    ha="left",
    va="center",
)

# Acceleration (text moved left to avoid the curve)
ax.annotate(
    "Acceleration:\n• Complements improve, costs fall\n• Barriers lapse (e.g., renewal cycles)\n• Demonstrated ROI spreads via networks",
    xy=(t0, (L / (1 + np.exp(-k * (t0 - t0)))) * 100),
    xytext=(1.8, 82),  # <-- shift this further left/right if needed
    arrowprops=dict(arrowstyle="->"),
    fontsize=9,
    ha="left",
    va="center",
)

# Late saturation
ax.annotate(
    "Saturation:\n• Market approaches capacity\n• Remaining adopters are harder to convert\n• Adoption rates slow down",
    xy=(8.5, (L / (1 + np.exp(-k * (8.5 - t0)))) * 100),
    xytext=(6.6, 25),
    arrowprops=dict(arrowstyle="->"),
    fontsize=9,
    ha="left",
    va="center",
)

# Remove numbers/ticks on the x-axis
ax.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)

plt.tight_layout()
# Optional: save instead of (or in addition to) showing
# plt.savefig("s_curve_adoption_v2.png", dpi=200, bbox_inches="tight")
plt.show()