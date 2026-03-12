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

mcp = FastMCP("auto_sklearn_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(
    name="autosklearn_list_metrics",
    description="List available Auto-sklearn metrics for a task type.",
)
def autosklearn_list_metrics(task: str) -> Dict[str, Any]:
    """
    Return metric names supported by auto-sklearn.

    Parameters:
    - task: One of "classification", "regression", or "all".

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        from autosklearn import metrics as askl_metrics

        cls_metrics = [
            "accuracy",
            "balanced_accuracy",
            "roc_auc",
            "average_precision",
            "log_loss",
            "precision",
            "recall",
            "f1",
        ]
        reg_metrics = [
            "mean_absolute_error",
            "mean_squared_error",
            "root_mean_squared_error",
            "mean_squared_log_error",
            "median_absolute_error",
            "r2",
        ]

        task_norm = task.strip().lower()
        if task_norm == "classification":
            return _ok(cls_metrics)
        if task_norm == "regression":
            return _ok(reg_metrics)
        if task_norm == "all":
            return _ok({"classification": cls_metrics, "regression": reg_metrics})

        # soft validation against imported module existence
        _ = askl_metrics
        return _err("Invalid task. Use 'classification', 'regression', or 'all'.")
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="autosklearn_fit_classification",
    description="Train an AutoSklearnClassifier and return basic fit summary.",
)
def autosklearn_fit_classification(
    X: List[List[float]],
    y: List[Any],
    time_left_for_this_task: int = 60,
    per_run_time_limit: int = 30,
    metric: str = "accuracy",
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Fit AutoSklearnClassifier on provided tabular data.

    Parameters:
    - X: 2D feature matrix.
    - y: Target labels.
    - time_left_for_this_task: Total AutoML budget (seconds).
    - per_run_time_limit: Per-model budget (seconds).
    - metric: Metric name ("accuracy", "balanced_accuracy", "roc_auc", "log_loss", etc.).
    - seed: Random seed.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        import numpy as np
        import autosklearn.classification as askl_cls
        from autosklearn import metrics as askl_metrics

        metric_obj = getattr(askl_metrics, metric, None)
        if metric_obj is None:
            return _err(f"Unknown classification metric: {metric}")

        model = askl_cls.AutoSklearnClassifier(
            time_left_for_this_task=time_left_for_this_task,
            per_run_time_limit=per_run_time_limit,
            metric=metric_obj,
            seed=seed,
        )
        X_np = np.asarray(X)
        y_np = np.asarray(y)
        model.fit(X_np, y_np)

        result = {
            "n_samples": int(X_np.shape[0]),
            "n_features": int(X_np.shape[1]) if X_np.ndim > 1 else 1,
            "classes": [str(c) for c in getattr(model, "classes_", [])],
            "cv_results_keys": sorted(list(getattr(model, "cv_results_", {}).keys())),
            "sprint_statistics": model.sprint_statistics(),
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="autosklearn_fit_regression",
    description="Train an AutoSklearnRegressor and return basic fit summary.",
)
def autosklearn_fit_regression(
    X: List[List[float]],
    y: List[float],
    time_left_for_this_task: int = 60,
    per_run_time_limit: int = 30,
    metric: str = "r2",
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Fit AutoSklearnRegressor on provided tabular data.

    Parameters:
    - X: 2D feature matrix.
    - y: Numeric target values.
    - time_left_for_this_task: Total AutoML budget (seconds).
    - per_run_time_limit: Per-model budget (seconds).
    - metric: Regression metric name ("r2", "mean_squared_error", etc.).
    - seed: Random seed.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        import numpy as np
        import autosklearn.regression as askl_reg
        from autosklearn import metrics as askl_metrics

        metric_obj = getattr(askl_metrics, metric, None)
        if metric_obj is None:
            return _err(f"Unknown regression metric: {metric}")

        model = askl_reg.AutoSklearnRegressor(
            time_left_for_this_task=time_left_for_this_task,
            per_run_time_limit=per_run_time_limit,
            metric=metric_obj,
            seed=seed,
        )
        X_np = np.asarray(X)
        y_np = np.asarray(y)
        model.fit(X_np, y_np)

        result = {
            "n_samples": int(X_np.shape[0]),
            "n_features": int(X_np.shape[1]) if X_np.ndim > 1 else 1,
            "cv_results_keys": sorted(list(getattr(model, "cv_results_", {}).keys())),
            "sprint_statistics": model.sprint_statistics(),
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="autosklearn_predict",
    description="Fit-and-predict helper for classification or regression.",
)
def autosklearn_predict(
    task: str,
    X_train: List[List[float]],
    y_train: List[Any],
    X_test: List[List[float]],
    time_left_for_this_task: int = 60,
    per_run_time_limit: int = 30,
    metric: Optional[str] = None,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Train auto-sklearn model and predict on test data.

    Parameters:
    - task: "classification" or "regression".
    - X_train: Training features.
    - y_train: Training targets.
    - X_test: Test features.
    - time_left_for_this_task: Total AutoML budget (seconds).
    - per_run_time_limit: Per-model budget (seconds).
    - metric: Optional metric name.
    - seed: Random seed.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        import numpy as np
        from autosklearn import metrics as askl_metrics

        task_norm = task.strip().lower()
        X_tr = np.asarray(X_train)
        y_tr = np.asarray(y_train)
        X_te = np.asarray(X_test)

        if task_norm == "classification":
            import autosklearn.classification as askl_cls

            metric_name = metric or "accuracy"
            metric_obj = getattr(askl_metrics, metric_name, None)
            if metric_obj is None:
                return _err(f"Unknown classification metric: {metric_name}")

            model = askl_cls.AutoSklearnClassifier(
                time_left_for_this_task=time_left_for_this_task,
                per_run_time_limit=per_run_time_limit,
                metric=metric_obj,
                seed=seed,
            )
            model.fit(X_tr, y_tr)
            preds = model.predict(X_te).tolist()
            return _ok(preds)

        if task_norm == "regression":
            import autosklearn.regression as askl_reg

            metric_name = metric or "r2"
            metric_obj = getattr(askl_metrics, metric_name, None)
            if metric_obj is None:
                return _err(f"Unknown regression metric: {metric_name}")

            model = askl_reg.AutoSklearnRegressor(
                time_left_for_this_task=time_left_for_this_task,
                per_run_time_limit=per_run_time_limit,
                metric=metric_obj,
                seed=seed,
            )
            model.fit(X_tr, y_tr)
            preds = model.predict(X_te).tolist()
            return _ok(preds)

        return _err("Invalid task. Use 'classification' or 'regression'.")
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(
    name="autosklearn_get_models_summary",
    description="Train a model and return detailed ensemble/model summary.",
)
def autosklearn_get_models_summary(
    task: str,
    X: List[List[float]],
    y: List[Any],
    time_left_for_this_task: int = 60,
    per_run_time_limit: int = 30,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Fit auto-sklearn and return ensemble and model leaderboard-style information.

    Parameters:
    - task: "classification" or "regression".
    - X: Feature matrix.
    - y: Target vector.
    - time_left_for_this_task: Total AutoML budget.
    - per_run_time_limit: Per-model budget.
    - seed: Random seed.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        import numpy as np

        X_np = np.asarray(X)
        y_np = np.asarray(y)
        task_norm = task.strip().lower()

        if task_norm == "classification":
            import autosklearn.classification as askl_cls

            model = askl_cls.AutoSklearnClassifier(
                time_left_for_this_task=time_left_for_this_task,
                per_run_time_limit=per_run_time_limit,
                seed=seed,
            )
        elif task_norm == "regression":
            import autosklearn.regression as askl_reg

            model = askl_reg.AutoSklearnRegressor(
                time_left_for_this_task=time_left_for_this_task,
                per_run_time_limit=per_run_time_limit,
                seed=seed,
            )
        else:
            return _err("Invalid task. Use 'classification' or 'regression'.")

        model.fit(X_np, y_np)

        result = {
            "show_models": model.show_models(),
            "leaderboard": model.leaderboard().to_dict(orient="records")
            if hasattr(model.leaderboard(), "to_dict")
            else str(model.leaderboard()),
            "sprint_statistics": model.sprint_statistics(),
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()