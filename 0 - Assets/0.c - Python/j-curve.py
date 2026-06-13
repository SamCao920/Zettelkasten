[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20originate%20in%20the%20agent,%20a%20persisting%20entity%20and%20not%20an%20event.md)[](Free%20actions%20originate%20in%20the%20agent,%20a%20persisting%20entity%20and%20not%20an%20event.md)"""
Data-anchored J-curves for Steam (UK TFP growth TFPGUKA), Electricity (US 1899–1937 rates),
IT & AI era (US OPHNFB). Starts at t=0 and matches dot colors to fitted lines.

Sources:
- TFPGUKA (Bank of England via FRED): https://fred.stlouisfed.org/series/TFPGUKA
- OPHNFB (BLS via FRED): https://fred.stlouisfed.org/series/OPHNFB
- 1920s US productivity summary (EH.Net): https://eh.net/encyclopedia/the-u-s-economy-in-the-1920s/
- Productivity J-curve theory: Brynjolfsson, Rock & Syverson, NBER w25148.
"""

import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from scipy.optimize import curve_fit

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"

# --- put this near the top, after imports ---
import matplotlib as mpl
mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],  # fallback list
    "mathtext.fontset": "dejavuserif",
})

# ---------- helpers
def fetch_fred_series(series_id):
    """Return DataFrame with ['date','value'] from FRED CSV. Handles alt headers & HTML."""
    url = FRED_CSV.format(series_id=series_id)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as resp:
        txt = resp.read().decode("utf-8", errors="replace")
    if "<html" in txt.lower():
        raise RuntimeError(f"FRED returned HTML for {series_id}. Download CSV manually from the series page.")
    df = pd.read_csv(io.StringIO(txt), encoding="utf-8-sig")
    cols = [c.strip() for c in df.columns]
    df.columns = cols
    date_col = next((c for c in cols if c.lower() in ("date","observation_date")), cols[0])
    value_col = next(c for c in cols if c != date_col)
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    out = pd.DataFrame({"date": df[date_col], "value": pd.to_numeric(df[value_col], errors="coerce")})
    return out.dropna().sort_values("date").reset_index(drop=True)

def rebased(series_df, base_date, to_annual=True):
    """Rebase to 100 at base_date (nearest obs)."""
    s = series_df.copy()
    base_date = pd.to_datetime(base_date)
    idx = (s["date"] - base_date).abs().idxmin()
    base_val = float(s.loc[idx, "value"])
    s["index"] = 100.0 * s["value"] / base_val
    if to_annual:
        s = s.set_index("date")["index"].resample("A").mean().to_frame("index").reset_index()
    return s

def logistic(x, L, k, tau):
    return L / (1.0 + np.exp(-k*(x - tau)))

def jcurve(t, L, k, tau, D, lamb):
    # baseline 100 + logistic benefits - decaying early dip
    return 100.0 + logistic(t, L, k, tau) - D*np.exp(-lamb*t)

def fit_jcurve(t, y, p0=None, bounds=None):
    x = np.asarray(t, float); y = np.asarray(y, float)
    if p0 is None:  p0 = (20.0, 0.2, x.mean(), 5.0, 0.3)
    if bounds is None: bounds = ((0,1e-4,-50,0,1e-4),(200,5.0,100,50,5.0))
    params, _ = curve_fit(jcurve, x, y, p0=p0, bounds=bounds, maxfev=200000)
    return params

# ---------- STEAM (UK): cumulate annual TFP growth (TFPGUKA) to a level, base 1760
uk = fetch_fred_series("TFPGUKA")  # 1761–2016 annual % growth
uk = uk[(uk["date"].dt.year>=1761) & (uk["date"].dt.year<=1910)].copy()
uk["g"] = uk["value"]/100.0
levels = [100.0*(1.0+uk["g"].iloc[0])]
for i in range(1,len(uk)): levels.append(levels[-1]*(1.0+uk["g"].iloc[i]))
steam_df = pd.DataFrame({"Year": uk["date"].dt.year.values, "Index": levels})
steam_df["t"] = steam_df["Year"] - 1760

# ELECTRICITY (US): base t=0 at 1899 so we see the slow build-up, then the surge
base_elec = 1899
yrs = np.arange(1899, 1938)
idx = []
level = 100.0
for y in yrs:
    idx.append(level)
    level *= 1.012 if y < 1919 else 1.035  # EH.Net: ~1.2%/yr to 1919, ~3.5%/yr after
elec_df = pd.DataFrame({"Year": yrs, "Index": np.array(idx)})
elec_df["t"] = elec_df["Year"] - base_elec

# ---------- IT (US): OPHNFB, base 1973
oph = fetch_fred_series("OPHNFB")  # Nonfarm business labor productivity (index 2017=100)
it = rebased(oph, base_date="1973-01-01", to_annual=True)
it_df = it[(it["date"].dt.year>=1973) & (it["date"].dt.year<=2010)].copy()
it_df["Year"] = it_df["date"].dt.year
it_df["t"] = it_df["Year"] - 1973
it_df.rename(columns={"index":"Index"}, inplace=True)

# ---------- AI era (US): same series, base 2019Q4; keep quarterly
ai = rebased(oph, base_date="2019-12-31", to_annual=False)
ai = ai[ai["date"]>=pd.Timestamp("2019-12-31")].copy()
ai["t"] = (ai["date"] - pd.Timestamp("2019-12-31")).dt.days/365.25
ai.rename(columns={"index":"Index"}, inplace=True)

# ---------- Fit J-curves
steam_params = fit_jcurve(steam_df["t"], steam_df["Index"])
elec_params  = fit_jcurve(elec_df["t"],  elec_df["Index"],  p0=(50,0.25,6,8,0.2))
it_params    = fit_jcurve(it_df["t"],    it_df["Index"],    p0=(25,0.20,15,4,0.25))
ai_params    = fit_jcurve(ai["t"],       ai["Index"],       p0=(8,0.8,1.5,1.0,1.0),
                          bounds=((0,1e-4,-2,0,1e-4),(50,5,8,10,5)))

# --- plotting block (replace your existing one) ---
fig, ax = plt.subplots(figsize=(9, 5.5))

def plot_fit(df_t, y, params, label):
    xgrid = np.linspace(df_t.min(), df_t.max(), 400)
    # draw fitted line first, capture its color
    (line,) = ax.plot(xgrid, jcurve(xgrid, *params), label=label, linewidth=2.2, zorder=3)
    color = line.get_color()
    # now the data points: same color, *more* transparent, behind the line
    ax.scatter(df_t, y, s=18, alpha=0.12, edgecolors="none", color=color, zorder=1)

plot_fit(steam_df["t"], steam_df["Index"], steam_params, "Steam (UK TFP level)")
plot_fit(elec_df["t"],  elec_df["Index"],  elec_params,  "Electricity (US labor prod.)")
plot_fit(it_df["t"],    it_df["Index"],    it_params,    "Computers/IT (US labor prod.)")
plot_fit(ai["t"],       ai["Index"],       ai_params,    "AI era (US labor prod., 2019Q4=100)")

ax.axhline(100, linestyle="--", linewidth=1.0)
ax.set_xlim(left=0)
ax.set_xlabel("Years since 'introduction' (base year)")
ax.set_ylabel("Measured productivity index (base=100)")
ax.set_title("Data-anchored J-curves (fitted) for Steam, Electricity, IT, and AI")
ax.legend(framealpha=0.9)
plt.tight_layout()
plt.show()

# Print fitted parameters for reference
for lab, p in [("Steam", steam_params), ("Electricity", elec_params), ("IT", it_params), ("AI", ai_params)]:
    L,k,tau,D,lamb = p
    print(f"{lab} params: L={L:.2f}, k={k:.3f}, tau={tau:.2f}, D={D:.2f}, lambda={lamb:.3f}")
    
    