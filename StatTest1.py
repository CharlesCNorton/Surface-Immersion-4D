import numpy as np
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
from statsmodels.tsa.arima.model import ARIMA
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import Ridge, HuberRegressor
from sklearn.utils import resample
import matplotlib.pyplot as plt

# -----------------------------------
# STEP 1: DATA (example invariants for each genus, replace with actual computed invariants)
# -----------------------------------
genus = np.arange(0, 21)
total_invariant = np.array([0, 2795/6, 3589/3, 43821/20, 51748/15, 208855/42,
                            94635/14, 634361/72, 500648/45, 1507491/110,
                            546065/33, 3066085/156, 2095308/91, 5598671/210,
                            1833559/60, 9444465/272, 5989840/153, 14993371/342,
                            4635549/95, 22685981/420, 13743860/231])

# -----------------------------------
# STEP 2: OLS Regression
# -----------------------------------
X = sm.add_constant(genus)
ols_model = OLS(total_invariant, X)
ols_results = ols_model.fit()

print("--- OLS Regression Results ---")
print(ols_results.summary())

# -----------------------------------
# STEP 3: Autoregressive Model (ARIMA)
# -----------------------------------
arima_model = ARIMA(total_invariant, order=(1, 1, 0))
arima_fit = arima_model.fit()

print("\n--- ARIMA Model Summary ---")
print(arima_fit.summary())

# -----------------------------------
# STEP 4: Ridge Regression
# -----------------------------------
ridge = Ridge(alpha=1.0)
ridge.fit(genus.reshape(-1, 1), total_invariant)
ridge_coefs = ridge.coef_
print(f"\nRidge Regression Coefficients: {ridge_coefs}")

# -----------------------------------
# STEP 5: Robust Regression (Huber)
# -----------------------------------
huber_regressor = HuberRegressor()
huber_regressor.fit(genus.reshape(-1, 1), total_invariant)
huber_predictions = huber_regressor.predict(genus.reshape(-1, 1))
print(f"\nHuber Regression Coefficients: {huber_regressor.coef_}")

# -----------------------------------
# STEP 6: Monte Carlo Simulations
# -----------------------------------
def monte_carlo_simulation(data, n_simulations=1000):
    simulated_results = []
    for _ in range(n_simulations):
        sample = resample(data)
        ols_model = OLS(sample, X)
        simulated_results.append(ols_model.fit().params)
    return np.array(simulated_results)

mc_simulations = monte_carlo_simulation(total_invariant)

# Monte Carlo Analysis: Mean and Confidence Intervals
mc_mean = np.mean(mc_simulations, axis=0)
mc_std = np.std(mc_simulations, axis=0)
mc_conf_int = np.percentile(mc_simulations, [2.5, 97.5], axis=0)

print(f"\nMonte Carlo Mean: {mc_mean}")
print(f"Monte Carlo Confidence Intervals (95%): {mc_conf_int}")

# -----------------------------------
# STEP 7: Cross-Validation and Bootstrap Confidence Intervals
# -----------------------------------
cv = KFold(n_splits=5, shuffle=True)
ridge_cv_scores = cross_val_score(ridge, genus.reshape(-1, 1), total_invariant, cv=cv)
huber_cv_scores = cross_val_score(huber_regressor, genus.reshape(-1, 1), total_invariant, cv=cv)

print(f"\nRidge Cross-Validation Scores: {ridge_cv_scores}")
print(f"Ridge Cross-Validation Mean: {ridge_cv_scores.mean()}")

print(f"\nHuber Cross-Validation Scores: {huber_cv_scores}")
print(f"Huber Cross-Validation Mean: {huber_cv_scores.mean()}")

# Bootstrap Confidence Intervals (Ridge)
ridge_bootstrap_intervals = []
for _ in range(1000):
    sample_genus, sample_invariants = resample(genus, total_invariant)
    ridge.fit(sample_genus.reshape(-1, 1), sample_invariants)
    ridge_bootstrap_intervals.append(ridge.coef_)

ridge_bootstrap_intervals = np.array(ridge_bootstrap_intervals)
ci_low, ci_high = np.percentile(ridge_bootstrap_intervals, [0.5, 99.5], axis=0)

print(f"\nBootstrapped Confidence Interval (Ridge, 99%): {ci_low}, {ci_high}")

# -----------------------------------
# STEP 8: Visualization
# -----------------------------------
plt.figure(figsize=(10, 6))
plt.plot(genus, total_invariant, 'o-', label="True Invariants", markersize=6)
plt.plot(genus, ols_results.predict(X), '--', label="OLS Fit")
plt.plot(genus, huber_predictions, '-.', label="Huber Robust Fit")
plt.title("Genus vs Total Invariant")
plt.xlabel("Genus")
plt.ylabel("Total Invariant")
plt.legend()
plt.grid(True)
plt.show()
