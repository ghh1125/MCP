import os
import sys
from typing import Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

mcp = FastMCP("sktime_service")


def _safe_execute(func):
    try:
        return {"success": True, "result": func(), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="list_estimators",
    description="List sktime estimators with optional filtering by estimator type and tag.",
)
def list_estimators(
    estimator_types: str = "",
    filter_tags: str = "",
    as_dataframe: bool = False,
) -> dict[str, Any]:
    """
    List available estimators registered in sktime.

    Parameters:
    - estimator_types: Optional comma-separated estimator types (e.g., 'forecaster,classifier').
    - filter_tags: Optional comma-separated key=value tag filters (e.g., 'capability:multivariate=True').
    - as_dataframe: If True, return tabular records when available.

    Returns:
    - Dictionary with success/result/error fields.
    """
    def _run():
        from sktime.registry import all_estimators

        est_types = [x.strip() for x in estimator_types.split(",") if x.strip()] or None

        tag_dict: dict[str, Any] | None = None
        if filter_tags.strip():
            tag_dict = {}
            for item in filter_tags.split(","):
                item = item.strip()
                if not item or "=" not in item:
                    continue
                key, value = item.split("=", 1)
                v = value.strip()
                if v.lower() in {"true", "false"}:
                    parsed: Any = v.lower() == "true"
                else:
                    parsed = v
                tag_dict[key.strip()] = parsed

        results = all_estimators(
            estimator_types=est_types,
            filter_tags=tag_dict,
            as_dataframe=as_dataframe,
            return_names=True,
        )
        if hasattr(results, "to_dict"):
            return results.to_dict(orient="records")
        return results

    return _safe_execute(_run)


@mcp.tool(
    name="load_dataset",
    description="Load built-in sktime datasets for forecasting/classification/regression tasks.",
)
def load_dataset(name: str, split: str = "TRAIN", return_X_y: bool = True) -> dict[str, Any]:
    """
    Load a built-in sktime dataset.

    Parameters:
    - name: Dataset name (e.g., 'airline', 'basic_motions', 'gunpoint', 'tecator').
    - split: Dataset split for panel datasets ('TRAIN' or 'TEST').
    - return_X_y: Return (X, y) where applicable.

    Returns:
    - Dictionary with success/result/error fields.
    """
    def _run():
        import sktime.datasets as ds

        lname = name.strip().lower()

        forecasting_loaders = {
            "airline": ds.load_airline,
            "lynx": ds.load_lynx,
            "shampoo_sales": ds.load_shampoo_sales,
            "longley": ds.load_longley,
            "macroeconomic": ds.load_macroeconomic,
        }

        classification_loaders = {
            "basic_motions": ds.load_basic_motions,
            "gunpoint": ds.load_gunpoint,
            "arrow_head": ds.load_arrow_head,
            "italy_power_demand": ds.load_italy_power_demand,
            "japanese_vowels": ds.load_japanese_vowels,
            "osuleaf": ds.load_osuleaf,
            "acsf1": ds.load_acsf1,
        }

        regression_loaders = {"tecator": ds.load_tecator}

        if lname in forecasting_loaders:
            y = forecasting_loaders[lname]()
            return {"dataset": lname, "type": "forecasting", "length": len(y)}

        if lname in classification_loaders:
            X, y = classification_loaders[lname](split=split, return_X_y=return_X_y)
            return {
                "dataset": lname,
                "type": "classification",
                "n_instances": len(y),
                "n_labels": len(set(y)),
            }

        if lname in regression_loaders:
            X, y = regression_loaders[lname](split=split, return_X_y=return_X_y)
            return {
                "dataset": lname,
                "type": "regression",
                "n_instances": len(y),
            }

        raise ValueError(f"Unsupported dataset name: {name}")

    return _safe_execute(_run)


@mcp.tool(
    name="forecast_with_naive",
    description="Fit NaiveForecaster on a univariate series and produce point forecasts.",
)
def forecast_with_naive(dataset_name: str = "airline", fh: str = "1,2,3,4,5,6") -> dict[str, Any]:
    """
    Forecast a built-in time series using NaiveForecaster.

    Parameters:
    - dataset_name: Built-in forecasting dataset name (currently supports 'airline', 'lynx', 'shampoo_sales').
    - fh: Comma-separated forecasting horizon integers.

    Returns:
    - Dictionary with success/result/error fields.
    """
    def _run():
        from sktime.datasets import load_airline, load_lynx, load_shampoo_sales
        from sktime.forecasting.naive import NaiveForecaster

        loaders = {
            "airline": load_airline,
            "lynx": load_lynx,
            "shampoo_sales": load_shampoo_sales,
        }
        key = dataset_name.strip().lower()
        if key not in loaders:
            raise ValueError(f"Unsupported dataset: {dataset_name}")

        y = loaders[key]()
        fh_values = [int(x.strip()) for x in fh.split(",") if x.strip()]
        if not fh_values:
            raise ValueError("fh must contain at least one integer step.")

        model = NaiveForecaster(strategy="last")
        model.fit(y)
        preds = model.predict(fh=fh_values)

        return {
            "dataset": key,
            "fh": fh_values,
            "predictions": [float(v) for v in preds.tolist()],
        }

    return _safe_execute(_run)


@mcp.tool(
    name="classify_with_dummy",
    description="Train and evaluate DummyClassifier on a built-in classification dataset.",
)
def classify_with_dummy(dataset_name: str = "gunpoint", split_train: str = "TRAIN", split_test: str = "TEST") -> dict[str, Any]:
    """
    Fit DummyClassifier and evaluate simple accuracy on a selected classification dataset.

    Parameters:
    - dataset_name: One of 'gunpoint', 'basic_motions', 'arrow_head', 'italy_power_demand'.
    - split_train: Training split name.
    - split_test: Test split name.

    Returns:
    - Dictionary with success/result/error fields.
    """
    def _run():
        from sktime.classification.dummy import DummyClassifier
        from sktime.datasets import (
            load_arrow_head,
            load_basic_motions,
            load_gunpoint,
            load_italy_power_demand,
        )

        loaders = {
            "gunpoint": load_gunpoint,
            "basic_motions": load_basic_motions,
            "arrow_head": load_arrow_head,
            "italy_power_demand": load_italy_power_demand,
        }

        key = dataset_name.strip().lower()
        if key not in loaders:
            raise ValueError(f"Unsupported dataset: {dataset_name}")

        X_train, y_train = loaders[key](split=split_train, return_X_y=True)
        X_test, y_test = loaders[key](split=split_test, return_X_y=True)

        clf = DummyClassifier(strategy="prior")
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

        correct = sum(int(a == b) for a, b in zip(y_test, y_pred))
        acc = correct / len(y_test) if len(y_test) else 0.0

        return {
            "dataset": key,
            "n_test": len(y_test),
            "accuracy": acc,
        }

    return _safe_execute(_run)


@mcp.tool(
    name="compute_distance",
    description="Compute pairwise time-series distance using sktime distances API.",
)
def compute_distance(metric: str = "dtw") -> dict[str, Any]:
    """
    Compute distance between two simple sequences.

    Parameters:
    - metric: Distance metric name (e.g., 'dtw', 'euclidean', 'erp', 'msm').

    Returns:
    - Dictionary with success/result/error fields.
    """
    def _run():
        from sktime.distances import distance
        import numpy as np

        x = np.array([1.0, 2.0, 3.0, 2.0, 1.0])
        y = np.array([1.0, 1.5, 2.5, 2.0, 1.0])

        d = distance(x, y, metric=metric)
        return {"metric": metric, "distance": float(d)}

    return _safe_execute(_run)


@mcp.tool(
    name="transform_series_features",
    description="Generate summary features from a univariate series using SummaryTransformer.",
)
def transform_series_features(dataset_name: str = "airline") -> dict[str, Any]:
    """
    Extract feature summaries from a forecasting series.

    Parameters:
    - dataset_name: One of 'airline', 'lynx', 'shampoo_sales'.

    Returns:
    - Dictionary with success/result/error fields.
    """
    def _run():
        import pandas as pd
        from sktime.datasets import load_airline, load_lynx, load_shampoo_sales
        from sktime.transformations.series.summarize import SummaryTransformer

        loaders = {
            "airline": load_airline,
            "lynx": load_lynx,
            "shampoo_sales": load_shampoo_sales,
        }

        key = dataset_name.strip().lower()
        if key not in loaders:
            raise ValueError(f"Unsupported dataset: {dataset_name}")

        y = loaders[key]()
        df = pd.DataFrame({"y": y.values}, index=y.index)
        transformer = SummaryTransformer(summary_function=("mean", "std", "min", "max"))
        Xt = transformer.fit_transform(df)

        return {"dataset": key, "features": Xt.to_dict(orient="records")[0]}

    return _safe_execute(_run)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()