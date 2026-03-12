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
from pmdarima import __version__ as pmdarima_version
from pmdarima.arima import ARIMA, auto_arima
from pmdarima.datasets import load_airpassengers, load_ausbeer, load_wineind
from pmdarima.metrics import smape
from pmdarima.model_selection import RollingForecastCV, cross_val_score
from pmdarima.pipeline import Pipeline
from pmdarima.preprocessing.exog import DateFeaturizer, FourierFeaturizer
from pmdarima.utils import acf, diff_inv, ndiffs

mcp = FastMCP("pmdarima_service")


@mcp.tool(name="get_package_info", description="Get basic package metadata and availability checks.")
def get_package_info() -> Dict[str, Any]:
    """
    Return package-level information for pmdarima.

    Returns:
        Dict[str, Any]:
            success: bool indicating whether metadata retrieval succeeded.
            result: metadata dictionary on success.
            error: error message on failure, else None.
    """
    try:
        result = {
            "package": "pmdarima",
            "version": pmdarima_version,
            "modules": ["arima", "datasets", "model_selection", "pipeline", "preprocessing", "utils"],
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="load_dataset", description="Load built-in pmdarima datasets.")
def load_dataset(dataset_name: str) -> Dict[str, Any]:
    """
    Load a named dataset from pmdarima.datasets.

    Parameters:
        dataset_name: One of 'airpassengers', 'ausbeer', or 'wineind'.

    Returns:
        Dict[str, Any]:
            success: bool for operation status.
            result: dataset values as a list on success.
            error: error message on failure, else None.
    """
    try:
        name = dataset_name.strip().lower()
        if name == "airpassengers":
            data = load_airpassengers()
        elif name == "ausbeer":
            data = load_ausbeer()
        elif name == "wineind":
            data = load_wineind()
        else:
            return {"success": False, "result": None, "error": "Unsupported dataset_name"}
        return {"success": True, "result": data.tolist(), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="fit_auto_arima", description="Fit an AutoARIMA model and return core model details.")
def fit_auto_arima(
    y: List[float],
    seasonal: bool = True,
    m: int = 1,
    d: Optional[int] = None,
    D: Optional[int] = None,
    max_p: int = 5,
    max_q: int = 5,
    max_P: int = 2,
    max_Q: int = 2,
    stepwise: bool = True,
    suppress_warnings: bool = True,
) -> Dict[str, Any]:
    """
    Fit pmdarima.auto_arima on a univariate series.

    Parameters:
        y: Target time-series values.
        seasonal: Whether to fit a seasonal model.
        m: Seasonal periodicity.
        d: Non-seasonal differencing order or None for auto.
        D: Seasonal differencing order or None for auto.
        max_p: Maximum AR order.
        max_q: Maximum MA order.
        max_P: Maximum seasonal AR order.
        max_Q: Maximum seasonal MA order.
        stepwise: Use stepwise search.
        suppress_warnings: Suppress fitting warnings.

    Returns:
        Dict[str, Any]:
            success: bool for operation status.
            result: model summary fields on success.
            error: error message on failure, else None.
    """
    try:
        model = auto_arima(
            y=y,
            seasonal=seasonal,
            m=m,
            d=d,
            D=D,
            max_p=max_p,
            max_q=max_q,
            max_P=max_P,
            max_Q=max_Q,
            stepwise=stepwise,
            suppress_warnings=suppress_warnings,
            error_action="ignore",
            trace=False,
        )
        result = {
            "order": model.order,
            "seasonal_order": model.seasonal_order,
            "aic": float(model.aic()),
            "bic": float(model.bic()),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="forecast_with_arima", description="Fit an ARIMA model with explicit order and produce forecast.")
def forecast_with_arima(
    y: List[float],
    p: int,
    d: int,
    q: int,
    seasonal_order_P: int = 0,
    seasonal_order_D: int = 0,
    seasonal_order_Q: int = 0,
    seasonal_m: int = 0,
    n_periods: int = 12,
) -> Dict[str, Any]:
    """
    Fit ARIMA(order=(p,d,q), seasonal_order=(P,D,Q,m)) and forecast n periods.

    Parameters:
        y: Target series values.
        p: AR order.
        d: Differencing order.
        q: MA order.
        seasonal_order_P: Seasonal AR order.
        seasonal_order_D: Seasonal differencing order.
        seasonal_order_Q: Seasonal MA order.
        seasonal_m: Seasonal period length.
        n_periods: Forecast horizon.

    Returns:
        Dict[str, Any]:
            success: bool for operation status.
            result: fitted model metrics and forecast on success.
            error: error message on failure, else None.
    """
    try:
        model = ARIMA(
            order=(p, d, q),
            seasonal_order=(seasonal_order_P, seasonal_order_D, seasonal_order_Q, seasonal_m),
            suppress_warnings=True,
        )
        model.fit(y)
        fcst = model.predict(n_periods=n_periods)
        result = {
            "order": (p, d, q),
            "seasonal_order": (seasonal_order_P, seasonal_order_D, seasonal_order_Q, seasonal_m),
            "aic": float(model.aic()),
            "bic": float(model.bic()),
            "forecast": fcst.tolist(),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="cross_validate_auto_arima", description="Run rolling cross-validation for AutoARIMA with SMAPE scoring.")
def cross_validate_auto_arima(
    y: List[float],
    h: int = 6,
    step: int = 1,
    initial: Optional[int] = None,
    seasonal: bool = False,
    m: int = 1,
) -> Dict[str, Any]:
    """
    Perform rolling forecast cross-validation using AutoARIMA and SMAPE.

    Parameters:
        y: Target series values.
        h: Forecast horizon for each CV fold.
        step: Number of periods to advance between folds.
        initial: Initial training size; if None, pmdarima default is used.
        seasonal: Whether AutoARIMA uses seasonal search.
        m: Seasonal periodicity.

    Returns:
        Dict[str, Any]:
            success: bool for operation status.
            result: fold scores and aggregate statistics on success.
            error: error message on failure, else None.
    """
    try:
        estimator = auto_arima(
            y=y,
            seasonal=seasonal,
            m=m,
            stepwise=True,
            suppress_warnings=True,
            error_action="ignore",
            trace=False,
        )
        cv = RollingForecastCV(h=h, step=step, initial=initial)
        scores = cross_val_score(estimator, y=y, cv=cv, scoring="smape")
        result = {
            "scores": scores.tolist(),
            "mean_score": float(scores.mean()) if len(scores) else None,
            "num_folds": int(len(scores)),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="compute_series_diagnostics", description="Compute diagnostics like ndiffs, ACF, and SMAPE against forecast.")
def compute_series_diagnostics(
    y_true: List[float],
    y_pred: Optional[List[float]] = None,
    acf_n_lags: int = 20,
    alpha: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Compute key diagnostics from pmdarima utilities and metrics.

    Parameters:
        y_true: Ground-truth time-series values.
        y_pred: Optional predicted values for SMAPE computation.
        acf_n_lags: Number of lags for ACF.
        alpha: Optional confidence alpha for ACF intervals.

    Returns:
        Dict[str, Any]:
            success: bool for operation status.
            result: diagnostics values on success.
            error: error message on failure, else None.
    """
    try:
        acf_vals = acf(y_true, nlags=acf_n_lags, alpha=alpha)
        nd = ndiffs(y_true)
        result: Dict[str, Any] = {"ndiffs": int(nd)}
        if isinstance(acf_vals, tuple):
            result["acf"] = acf_vals[0].tolist()
            result["acf_confint"] = acf_vals[1].tolist()
        else:
            result["acf"] = acf_vals.tolist()
            result["acf_confint"] = None

        if y_pred is not None:
            result["smape"] = float(smape(y_true, y_pred))
        else:
            result["smape"] = None

        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="invert_differences", description="Invert differenced values back to original scale.")
def invert_differences(x: List[float], differences: List[float], lag: int = 1) -> Dict[str, Any]:
    """
    Invert differenced sequence using pmdarima.utils.diff_inv.

    Parameters:
        x: Original historical values used as baseline.
        differences: Differenced values to invert.
        lag: Differencing lag.

    Returns:
        Dict[str, Any]:
            success: bool for operation status.
            result: reconstructed sequence on success.
            error: error message on failure, else None.
    """
    try:
        restored = diff_inv(differences, lag=lag, xi=x)
        return {"success": True, "result": restored.tolist(), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="build_feature_pipeline_forecast", description="Build a feature pipeline with Fourier and Date featurizers and forecast.")
def build_feature_pipeline_forecast(
    y: List[float],
    n_periods: int = 12,
    fourier_m: int = 12,
    fourier_k: int = 3,
) -> Dict[str, Any]:
    """
    Build and run a pmdarima Pipeline with exogenous preprocessors and AutoARIMA.

    Parameters:
        y: Target series values.
        n_periods: Forecast horizon.
        fourier_m: Seasonal period for Fourier terms.
        fourier_k: Number of Fourier components.

    Returns:
        Dict[str, Any]:
            success: bool for operation status.
            result: pipeline forecast and model order metadata on success.
            error: error message on failure, else None.
    """
    try:
        pipe = Pipeline(
            steps=[
                ("date", DateFeaturizer()),
                ("fourier", FourierFeaturizer(m=fourier_m, k=fourier_k)),
                (
                    "arima",
                    auto_arima(
                        y=y,
                        seasonal=False,
                        stepwise=True,
                        suppress_warnings=True,
                        error_action="ignore",
                        trace=False,
                    ),
                ),
            ]
        )
        pipe.fit(y)
        forecast = pipe.predict(n_periods=n_periods)
        arima_step = pipe.steps_[-1][1]
        result = {
            "forecast": forecast.tolist(),
            "order": arima_step.order,
            "seasonal_order": arima_step.seasonal_order,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()