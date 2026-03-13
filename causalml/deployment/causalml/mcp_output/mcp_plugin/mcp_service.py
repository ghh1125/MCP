import os
import sys
from typing import Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
import numpy as np
import pandas as pd

from causalml.dataset import make_uplift_classification
from causalml.inference.meta import (
    BaseSClassifier,
    BaseTClassifier,
    BaseXClassifier,
    BaseRClassifier,
    BaseSRegressor,
    BaseTRegressor,
    BaseXRegressor,
    BaseRRegressor,
)
from causalml.metrics import (
    qini_score,
    auuc_score,
    get_cumgain,
    get_qini,
    regression_metrics,
)
from causalml.propensity import ElasticNetPropensityModel
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

mcp = FastMCP("causalml_service")


def _ok(result):
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception):
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="generate_uplift_dataset", description="Generate a synthetic uplift classification dataset.")
def generate_uplift_dataset(
    n_samples: int = 1000,
    treatment_name: str = "treatment",
    y_name: str = "conversion",
    random_seed: int = 42,
) -> Dict:
    """
    Generate a synthetic uplift classification dataset.

    Parameters:
        n_samples: Number of rows to generate.
        treatment_name: Name used for treatment column in the returned DataFrame.
        y_name: Name used for outcome column in the returned DataFrame.
        random_seed: Random seed for reproducibility.

    Returns:
        Dictionary with success/result/error fields. On success, returns sampled rows and column names.
    """
    try:
        X, treatment, y, _ = make_uplift_classification(
            n_samples=n_samples,
            random_seed=random_seed,
        )
        X_df = pd.DataFrame(X)
        X_df[treatment_name] = treatment
        X_df[y_name] = y
        return _ok(
            {
                "shape": list(X_df.shape),
                "columns": [str(c) for c in X_df.columns.tolist()],
                "head": X_df.head(5).to_dict(orient="records"),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="fit_s_learner_classifier", description="Train an S-learner classifier and return uplift predictions.")
def fit_s_learner_classifier(
    n_samples: int = 1500,
    random_seed: int = 42,
    n_estimators: int = 100,
) -> Dict:
    """
    Train a classification S-learner on synthetic data and return CATE/uplift predictions.

    Parameters:
        n_samples: Number of synthetic samples.
        random_seed: Random seed for reproducibility.
        n_estimators: Number of trees in the RandomForestClassifier base learner.

    Returns:
        Dictionary with success/result/error fields. Result includes mean uplift and a prediction sample.
    """
    try:
        X, treatment, y, _ = make_uplift_classification(n_samples=n_samples, random_seed=random_seed)
        learner = BaseSClassifier(learner=RandomForestClassifier(n_estimators=n_estimators, random_state=random_seed))
        learner.fit(X=X, treatment=treatment, y=y)
        uplift = learner.predict(X)
        uplift_arr = np.asarray(uplift).reshape(-1)
        return _ok(
            {
                "n_predictions": int(uplift_arr.shape[0]),
                "uplift_mean": float(np.mean(uplift_arr)),
                "uplift_std": float(np.std(uplift_arr)),
                "uplift_head": uplift_arr[:10].tolist(),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="fit_t_learner_classifier", description="Train a T-learner classifier and return uplift predictions.")
def fit_t_learner_classifier(
    n_samples: int = 1500,
    random_seed: int = 42,
    n_estimators: int = 100,
) -> Dict:
    """
    Train a classification T-learner on synthetic data and return uplift predictions.

    Parameters:
        n_samples: Number of synthetic samples.
        random_seed: Random seed for reproducibility.
        n_estimators: Number of trees in the RandomForestClassifier base learner.

    Returns:
        Dictionary with success/result/error fields including prediction statistics.
    """
    try:
        X, treatment, y, _ = make_uplift_classification(n_samples=n_samples, random_seed=random_seed)
        learner = BaseTClassifier(learner=RandomForestClassifier(n_estimators=n_estimators, random_state=random_seed))
        learner.fit(X=X, treatment=treatment, y=y)
        uplift = learner.predict(X)
        uplift_arr = np.asarray(uplift).reshape(-1)
        return _ok(
            {
                "n_predictions": int(uplift_arr.shape[0]),
                "uplift_mean": float(np.mean(uplift_arr)),
                "uplift_std": float(np.std(uplift_arr)),
                "uplift_head": uplift_arr[:10].tolist(),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="fit_x_learner_classifier", description="Train an X-learner classifier and return uplift predictions.")
def fit_x_learner_classifier(
    n_samples: int = 1500,
    random_seed: int = 42,
    n_estimators: int = 100,
) -> Dict:
    """
    Train a classification X-learner on synthetic data and return uplift predictions.

    Parameters:
        n_samples: Number of synthetic samples.
        random_seed: Random seed for reproducibility.
        n_estimators: Number of trees in the RandomForestClassifier base learner.

    Returns:
        Dictionary with success/result/error fields including prediction statistics.
    """
    try:
        X, treatment, y, _ = make_uplift_classification(n_samples=n_samples, random_seed=random_seed)
        learner = BaseXClassifier(learner=RandomForestClassifier(n_estimators=n_estimators, random_state=random_seed))
        learner.fit(X=X, treatment=treatment, y=y)
        uplift = learner.predict(X)
        uplift_arr = np.asarray(uplift).reshape(-1)
        return _ok(
            {
                "n_predictions": int(uplift_arr.shape[0]),
                "uplift_mean": float(np.mean(uplift_arr)),
                "uplift_std": float(np.std(uplift_arr)),
                "uplift_head": uplift_arr[:10].tolist(),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="fit_r_learner_classifier", description="Train an R-learner classifier and return uplift predictions.")
def fit_r_learner_classifier(
    n_samples: int = 1500,
    random_seed: int = 42,
    n_estimators: int = 100,
) -> Dict:
    """
    Train a classification R-learner on synthetic data and return uplift predictions.

    Parameters:
        n_samples: Number of synthetic samples.
        random_seed: Random seed for reproducibility.
        n_estimators: Number of trees in the RandomForestClassifier base learner.

    Returns:
        Dictionary with success/result/error fields including prediction statistics.
    """
    try:
        X, treatment, y, _ = make_uplift_classification(n_samples=n_samples, random_seed=random_seed)
        learner = BaseRClassifier(learner=RandomForestClassifier(n_estimators=n_estimators, random_state=random_seed))
        learner.fit(X=X, treatment=treatment, y=y)
        uplift = learner.predict(X)
        uplift_arr = np.asarray(uplift).reshape(-1)
        return _ok(
            {
                "n_predictions": int(uplift_arr.shape[0]),
                "uplift_mean": float(np.mean(uplift_arr)),
                "uplift_std": float(np.std(uplift_arr)),
                "uplift_head": uplift_arr[:10].tolist(),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="estimate_propensity_scores", description="Estimate propensity scores using ElasticNet propensity model.")
def estimate_propensity_scores(
    n_samples: int = 2000,
    random_seed: int = 42,
    clip_min: float = 0.01,
    clip_max: float = 0.99,
) -> Dict:
    """
    Estimate treatment propensity scores.

    Parameters:
        n_samples: Number of synthetic samples.
        random_seed: Random seed for reproducibility.
        clip_min: Minimum clipping value for scores.
        clip_max: Maximum clipping value for scores.

    Returns:
        Dictionary with success/result/error fields containing summary statistics.
    """
    try:
        X, treatment, _, _ = make_uplift_classification(n_samples=n_samples, random_seed=random_seed)
        model = ElasticNetPropensityModel()
        model.fit(X, treatment)
        p = np.asarray(model.predict(X)).reshape(-1)
        p = np.clip(p, clip_min, clip_max)
        return _ok(
            {
                "n_scores": int(p.shape[0]),
                "mean": float(np.mean(p)),
                "std": float(np.std(p)),
                "min": float(np.min(p)),
                "max": float(np.max(p)),
                "head": p[:10].tolist(),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="evaluate_uplift_metrics", description="Compute Qini and AUUC uplift evaluation metrics.")
def evaluate_uplift_metrics(
    n_samples: int = 1500,
    random_seed: int = 42,
    n_estimators: int = 100,
) -> Dict:
    """
    Compute uplift metrics using a trained T-learner on synthetic data.

    Parameters:
        n_samples: Number of synthetic samples.
        random_seed: Random seed for reproducibility.
        n_estimators: Number of trees in the base classifier.

    Returns:
        Dictionary with success/result/error fields containing Qini/AUUC and top rows from cumulative gain/Qini tables.
    """
    try:
        X, treatment, y, _ = make_uplift_classification(n_samples=n_samples, random_seed=random_seed)
        learner = BaseTClassifier(learner=RandomForestClassifier(n_estimators=n_estimators, random_state=random_seed))
        learner.fit(X=X, treatment=treatment, y=y)
        uplift = np.asarray(learner.predict(X)).reshape(-1)

        df = pd.DataFrame(
            {
                "y": y,
                "w": treatment,
                "tau": uplift,
            }
        )
        qini = float(qini_score(df, outcome_col="y", treatment_col="w", treatment_effect_col="tau"))
        auuc = float(auuc_score(df, outcome_col="y", treatment_col="w", treatment_effect_col="tau"))
        cumgain = get_cumgain(df, outcome_col="y", treatment_col="w", treatment_effect_col="tau")
        qini_curve = get_qini(df, outcome_col="y", treatment_col="w", treatment_effect_col="tau")

        return _ok(
            {
                "qini_score": qini,
                "auuc_score": auuc,
                "cumgain_head": cumgain.head(5).reset_index(drop=True).to_dict(orient="records"),
                "qini_curve_head": qini_curve.head(5).reset_index(drop=True).to_dict(orient="records"),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="fit_regression_meta_learners", description="Train regression meta-learners on synthetic transformed data.")
def fit_regression_meta_learners(
    n_samples: int = 1200,
    random_seed: int = 42,
    n_estimators: int = 120,
) -> Dict:
    """
    Train S/T/X/R regression meta-learners on synthetic data converted to continuous outcome.

    Parameters:
        n_samples: Number of synthetic samples.
        random_seed: Random seed for reproducibility.
        n_estimators: Number of trees in RandomForestRegressor.

    Returns:
        Dictionary with success/result/error fields and mean uplift estimates by learner.
    """
    try:
        X, treatment, y, _ = make_uplift_classification(n_samples=n_samples, random_seed=random_seed)
        rng = np.random.default_rng(random_seed)
        y_cont = y.astype(float) + 0.1 * rng.normal(size=len(y))

        base_reg = RandomForestRegressor(n_estimators=n_estimators, random_state=random_seed)

        s_model = BaseSRegressor(learner=base_reg)
        t_model = BaseTRegressor(learner=base_reg)
        x_model = BaseXRegressor(learner=base_reg)
        r_model = BaseRRegressor(learner=base_reg)

        s_model.fit(X=X, treatment=treatment, y=y_cont)
        t_model.fit(X=X, treatment=treatment, y=y_cont)
        x_model.fit(X=X, treatment=treatment, y=y_cont)
        r_model.fit(X=X, treatment=treatment, y=y_cont)

        s_tau = np.asarray(s_model.predict(X)).reshape(-1)
        t_tau = np.asarray(t_model.predict(X)).reshape(-1)
        x_tau = np.asarray(x_model.predict(X)).reshape(-1)
        r_tau = np.asarray(r_model.predict(X)).reshape(-1)

        return _ok(
            {
                "s_learner_mean_tau": float(np.mean(s_tau)),
                "t_learner_mean_tau": float(np.mean(t_tau)),
                "x_learner_mean_tau": float(np.mean(x_tau)),
                "r_learner_mean_tau": float(np.mean(r_tau)),
            }
        )
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()