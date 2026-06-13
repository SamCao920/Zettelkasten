[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20originate%20in%20the%20agent,%20a%20persisting%20entity%20and%20not%20an%20event.md)[](Free%20actions%20originate%20in%20the%20agent,%20a%20persisting%20entity%20and%20not%20an%20event.md)# expected_value_menu.py
import numpy as np
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt
import sys

def payoff(T, f, tau):
    return (T - tau) * f(tau)

def maximize_payoff(T, f, a=0.0, b=None, ngrid=2001):
    if b is None:
        b = T

    # coarse grid to get a good bracket
    taus = np.linspace(a, b, ngrid)
    vals = np.array([payoff(T, f, t) for t in taus])
    i_best = int(np.nanargmax(vals))
    tau_guess = taus[i_best]

    # refine with bounded search
    def neg_obj(tau):
        # penalize out-of-domain or nan
        val = payoff(T, f, tau)
        return -val if np.isfinite(val) else np.inf

    res = minimize_scalar(neg_obj, bounds=(a, b), method='bounded')
    tau_star = res.x
    max_val = -res.fun
    return tau_star, max_val

def build_f(choice):
    if choice == "1":
        # Linear
        m = float(input("Enter slope m (f(tau) = 1 + m*tau): "))
        f = lambda tau: 1.0 + m * tau
        label = f"Linear: f(τ)=1+{m}τ"
        domain = (0.0, None)

    elif choice == "2":
        # Logarithmic
        a = float(input("Enter a: "))
        b = float(input("Enter b: "))
        def f(tau):
            x = 1.0 + b * tau
            return 1.0 + a * np.log(x) if x > 0 else np.nan
        label = f"Log: f(τ)=1+{a}·ln(1+{b}τ)"
        domain = ("log", b)  # we'll compute feasible upper bound later

    elif choice == "3":
        # Logistic (saturating S-curve)
        L  = float(input("Enter L (height): "))
        k  = float(input("Enter k (steepness): "))
        t0 = float(input("Enter tau0 (midpoint): "))
        f = lambda tau: 1.0 + L / (1.0 + np.exp(-k * (tau - t0)))
        label = f"Logistic: 1+{L}/(1+exp(-{k}(τ-{t0})))"
        domain = (0.0, None)

    elif choice == "4":
        # Saturating exponential approach
        L = float(input("Enter L (max additional gain): "))
        k = float(input("Enter k (rate): "))
        f = lambda tau: 1.0 + L * (1.0 - np.exp(-k * tau))
        label = f"Saturating exp: 1+{L}(1-exp(-{k}τ))"
        domain = (0.0, None)

    elif choice == "5":
        # Custom Python expression in tau
        print("Enter a Python expression in variable 'tau'. You can use 'np' for numpy.")
        print("Examples: '1 + 0.2*tau', '1 + np.log(1 + 0.5*tau)', '2 + np.sin(tau)'")
        expr = input("f(tau) = ")
        def f(tau):
            try:
                return eval(expr, {"np": np, "tau": tau})
            except Exception:
                return np.nan
        label = f"Custom: f(τ) = {expr}"
        domain = (0.0, None)

    else:
        print("Invalid choice.")
        sys.exit(1)

    return f, label, domain

def compute_domain(domain_spec, T):
    if domain_spec == (0.0, None):
        return 0.0, T
    if isinstance(domain_spec, tuple) and domain_spec[0] == "log":
        b = domain_spec[1]
        low = 0.0
        if b < 0:
            # need 1 + b*tau > 0 => tau < -1/b
            high = min(T, -1.0 / b - 1e-12)  # back off tiny epsilon
        else:
            high = T
        if high <= low:
            raise ValueError("No feasible tau domain for the chosen log parameters on [0, T].")
        return low, high
    # default
    low = domain_spec[0] if isinstance(domain_spec[0], (int, float)) else 0.0
    high = domain_spec[1] if isinstance(domain_spec[1], (int, float)) else T
    return max(0.0, low), min(T, high)

def plot_everything(T, f, label, a, b, tau_star, max_val):
    taus = np.linspace(a, b, 800)
    fvals = np.array([f(t) for t in taus])
    hvals = (T - taus) * fvals

    # Plot f(tau)
    plt.figure()
    plt.plot(taus, fvals)
    plt.xlabel("τ")
    plt.ylabel("f(τ)")
    plt.title(f"Effectiveness function\n{label}")
    plt.grid(True)

    # Plot payoff (T - tau) f(tau)
    plt.figure()
    plt.plot(taus, hvals, label="(T - τ) f(τ)")
    # mark tau*
    plt.axvline(tau_star, linestyle="--")
    plt.scatter([tau_star], [max_val])
    plt.text(tau_star, max_val, f"  τ*={tau_star:.3f}\n  max={max_val:.3f}", va="bottom")
    plt.xlabel("τ")
    plt.ylabel("(T - τ) f(τ)")
    plt.title("(T - τ) f(τ) with optimum marked")
    plt.grid(True)
    plt.legend()

    plt.show()

if __name__ == "__main__":
    # --- Inputs ---
    T = float(input("Enter time horizon T (>0): "))

    print("\nChoose f(τ):")
    print("1: Linear           f(τ) = 1 + m τ")
    print("2: Logarithmic      f(τ) = 1 + a ln(1 + b τ)")
    print("3: Logistic (S-curve) f(τ) = 1 + L / (1 + exp(-k (τ - τ0)))")
    print("4: Saturating exp   f(τ) = 1 + L (1 - exp(-k τ))")
    print("5: Custom (Python expression in τ)")
    choice = input("Enter choice (1–5): ").strip()

    f, label, domain_spec = build_f(choice)
    a, b = compute_domain(domain_spec, T)

    # --- Solve ---
    tau_star, max_val = maximize_payoff(T, f, a=a, b=b)

    # --- Report ---
    print("\n=== Results ===")
    print(f"Domain used: [{a:.6g}, {b:.6g}] (subset of [0, T])")
    print(f"Optimal τ*  : {tau_star:.10g}")
    print(f"Max payoff  : {max_val:.10g}")
    print(f"U_now       : {T:.10g}")
    print(f"Optimize better than act now?  {max_val > T}")

    # --- Visualize ---
    plot_everything(T, f, label, a, b, tau_star, max_val)
