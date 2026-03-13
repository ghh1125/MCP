import os
import sys
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.api import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.stattools import jarque_bera

mcp = FastMCP("statsmodels_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="ols_fit", description="Fit an OLS regression model and return summary metrics.")
def ols_fit(
    y: List[float],
    X: List[List[float]],
    add_constant: bool = True,
) -> Dict[str, Any]:
    """
    Fit an Ordinary Least Squares (OLS) model.

    Parameters:
    - y: Dependent variable values.
    - X: 2D feature matrix where each inner list is one observation.
    - add_constant: If True, prepends an intercept column.

    Returns:
    - Dictionary with success/result/error fields. Result contains coefficients,
      p-values, R-squared, adjusted R-squared, AIC, BIC, and observation count.
    """
    try:
        y_arr = np.asarray(y, dtype=float)
        X_arr = np.asarray(X, dtype=float)
        if add_constant:
            X_arr = sm.add_constant(X_arr, has_constant="add")
        model = sm.OLS(y_arr, X_arr).fit()
        return _ok(
            {
                "params": model.params.tolist(),
                "pvalues": model.pvalues.tolist(),
                "rsquared": float(model.rsquared),
                "rsquared_adj": float(model.rsquared_adj),
                "aic": float(model.aic),
                "bic": float(model.bic),
                "nobs": int(model.nobs),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="glm_fit", description="Fit a GLM model for common families (gaussian, binomial, poisson).")
def glm_fit(
    y: List[float],
    X: List[List[float]],
    family: str = "gaussian",
    add_constant: bool = True,
) -> Dict[str, Any]:
    """
    Fit a Generalized Linear Model (GLM).

    Parameters:
    - y: Response values.
    - X: 2D feature matrix.
    - family: One of 'gaussian', 'binomial', 'poisson'.
    - add_constant: If True, prepends an intercept column.

    Returns:
    - Dictionary with success/result/error fields. Result contains coefficients,
      standard errors, p-values, deviance, and observation count.
    """
    try:
        fam = family.lower().strip()
        if fam == "gaussian":
            fam_obj = sm.families.Gaussian()
        elif fam == "binomial":
            fam_obj = sm.families.Binomial()
        elif fam == "poisson":
            fam_obj = sm.families.Poisson()
        else:
            raise ValueError("family must be one of: gaussian, binomial, poisson")

        y_arr = np.asarray(y, dtype=float)
        X_arr = np.asarray(X, dtype=float)
        if add_constant:
            X_arr = sm.add_constant(X_arr, has_constant="add")
        model = sm.GLM(y_arr, X_arr, family=fam_obj).fit()
        return _ok(
            {
                "params": model.params.tolist(),
                "bse": model.bse.tolist(),
                "pvalues": model.pvalues.tolist(),
                "deviance": float(model.deviance),
                "nobs": int(model.nobs),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="logit_fit", description="Fit a logistic regression model.")
def logit_fit(
    y: List[int],
    X: List[List[float]],
    add_constant: bool = True,
    maxiter: int = 100,
) -> Dict[str, Any]:
    """
    Fit a Logit (binary logistic regression) model.

    Parameters:
    - y: Binary response values (0/1).
    - X: 2D feature matrix.
    - add_constant: If True, prepends an intercept column.
    - maxiter: Maximum optimizer iterations.

    Returns:
    - Dictionary with success/result/error fields. Result contains coefficients,
      p-values, pseudo R-squared, log-likelihood, and convergence flag.
    """
    try:
        y_arr = np.asarray(y, dtype=float)
        X_arr = np.asarray(X, dtype=float)
        if add_constant:
            X_arr = sm.add_constant(X_arr, has_constant="add")
        model = sm.Logit(y_arr, X_arr).fit(disp=0, maxiter=maxiter)
        return _ok(
            {
                "params": model.params.tolist(),
                "pvalues": model.pvalues.tolist(),
                "prsquared": float(model.prsquared),
                "llf": float(model.llf),
                "converged": bool(model.mle_retvals.get("converged", False)),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="arima_fit_forecast", description="Fit ARIMA model and forecast future values.")
def arima_fit_forecast(
    y: List[float],
    p: int = 1,
    d: int = 0,
    q: int = 0,
    steps: int = 5,
) -> Dict[str, Any]:
    """
    Fit an ARIMA model and produce forecasts.

    Parameters:
    - y: Univariate time series.
    - p: AR order.
    - d: Differencing order.
    - q: MA order.
    - steps: Number of forecast steps.

    Returns:
    - Dictionary with success/result/error fields. Result includes fitted params,
      AIC/BIC, and forecast values.
    """
    try:
        y_arr = np.asarray(y, dtype=float)
        model = ARIMA(y_arr, order=(p, d, q)).fit()
        forecast = model.forecast(steps=steps)
        return _ok(
            {
                "params": model.params.tolist(),
                "aic": float(model.aic),
                "bic": float(model.bic),
                "forecast": np.asarray(forecast).tolist(),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="seasonal_decompose", description="Perform additive or multiplicative seasonal decomposition.")
def seasonal_decompose(
    y: List[float],
    period: int,
    model: str = "additive",
) -> Dict[str, Any]:
    """
    Decompose a time series into trend/seasonal/residual components.

    Parameters:
    - y: Univariate time series.
    - period: Seasonal period length.
    - model: 'additive' or 'multiplicative'.

    Returns:
    - Dictionary with success/result/error fields. Result contains trend,
      seasonal, and residual arrays (NaNs converted to None).
    """
    try:
        from statsmodels.tsa.seasonal import seasonal_decompose as sm_seasonal_decompose

        y_arr = pd.Series(np.asarray(y, dtype=float))
        dec = sm_seasonal_decompose(y_arr, model=model, period=period, extrapolate_trend="freq")

        def clean(values: pd.Series) -> List[Optional[float]]:
            out: List[Optional[float]] = []
            for v in values.to_numpy():
                out.append(None if pd.isna(v) else float(v))
            return out

        return _ok(
            {
                "trend": clean(dec.trend),
                "seasonal": clean(dec.seasonal),
                "resid": clean(dec.resid),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="diagnostic_tests", description="Run Jarque-Bera and Ljung-Box diagnostic tests.")
def diagnostic_tests(
    residuals: List[float],
    lags: int = 10,
) -> Dict[str, Any]:
    """
    Run common residual diagnostics.

    Parameters:
    - residuals: Residual series from a fitted model.
    - lags: Number of lags for Ljung-Box test.

    Returns:
    - Dictionary with success/result/error fields. Result contains Jarque-Bera
      statistic/p-value/skew/kurtosis and Ljung-Box test table.
    """
    try:
        resid = np.asarray(residuals, dtype=float)
        jb_stat, jb_pvalue, skew, kurt = jarque_bera(resid)
        lb = acorr_ljungbox(resid, lags=[lags], return_df=True)
        return _ok(
            {
                "jarque_bera": {
                    "statistic": float(jb_stat),
                    "pvalue": float(jb_pvalue),
                    "skew": float(skew),
                    "kurtosis": float(kurt),
                },
                "ljung_box": lb.reset_index().to_dict(orient="records"),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="load_dataset", description="Load a built-in statsmodels dataset as records.")
def load_dataset(
    dataset_name: str,
    max_rows: int = 20,
) -> Dict[str, Any]:
    """
    Load a built-in dataset from statsmodels.datasets.

    Parameters:
    - dataset_name: Dataset module name (e.g., 'longley', 'macrodata', 'sunspots').
    - max_rows: Maximum number of rows to return.

    Returns:
    - Dictionary with success/result/error fields. Result contains dataset
      metadata and sample records.
    """
    try:
        import importlib

        ds_module = importlib.import_module(f"statsmodels.datasets.{dataset_name}.data")
        loaded = ds_module.load_pandas()
        df = loaded.data.copy()
        sample = df.head(max_rows).to_dict(orient="records")
        return _ok(
            {
                "dataset_name": dataset_name,
                "columns": list(df.columns),
                "nrows": int(df.shape[0]),
                "sample": sample,
            }
        )
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp