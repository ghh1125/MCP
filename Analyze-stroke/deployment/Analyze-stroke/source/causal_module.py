# Analyze/causal_module.py
import dowhy
from dowhy import CausalModel
import pandas as pd
import numpy as np
import warnings

class CausalAnalyzer:
    def __init__(self, data):
        self.data = data.copy()
        for col in self.data.columns:
            if self.data[col].dtype == bool:
                self.data[col] = self.data[col].astype(int)

    def define_causal_graph(self):
        """
        定义领域知识 DAG
        """
        causal_graph = """
        digraph {
            age -> hypertension;
            age -> heart_disease;
            age -> avg_glucose_level;
            age -> stroke;
            age -> ever_married; 
            age -> work_type;
            
            bmi -> hypertension;
            bmi -> heart_disease;
            bmi -> stroke;
            
            hypertension -> stroke;
            heart_disease -> stroke;
            avg_glucose_level -> stroke;
            
            work_type -> bmi;
            work_type -> hypertension;
            work_type -> stroke;
            
            smoking_status -> heart_disease;
            smoking_status -> stroke;
            
            Residence_type -> bmi;
            Residence_type -> stroke;
            
            gender -> stroke;
            gender -> smoking_status;
            
            ever_married -> stroke;
            ever_married -> bmi;
        }
        """
        return causal_graph.replace("\n", " ")

    def run_analysis(self, treatment_col, outcome_col='stroke'):
        print(f"\n=== Causal Analysis: Effect of '{treatment_col}' on '{outcome_col}' ===")
        
        warnings.filterwarnings("ignore")

        model = CausalModel(
            data=self.data,
            treatment=treatment_col,
            outcome=outcome_col,
            graph=self.define_causal_graph()
        )
        
        identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
        
        estimate = None
        try:
            print("[Causal] Attempting Propensity Score Stratification...")
            estimate = model.estimate_effect(
                identified_estimand,
                method_name="backdoor.propensity_score_stratification"
            )
        except Exception as e:
            error_msg = str(e)
            if "No common causes" in error_msg or "Propensity score" in error_msg:
                print(f"[Info] Switching to Linear Regression (Root Node/No Confounders detected).")
                estimate = model.estimate_effect(
                    identified_estimand,
                    method_name="backdoor.linear_regression"
                )
            else:
                print(f"[Error] Estimation failed: {e}")
                return 0.0

        if estimate is not None:
            print(f"\n[Result] Causal Estimate (ATE): {estimate.value:.4f}")
            print(f"[Interpretation] If '{treatment_col}' increases by 1 unit (or switches from 0 to 1),")
            print(f"                 the probability of '{outcome_col}' changes by {estimate.value:.4f}")

            print("\n[Causal] Refuting estimate (Random Common Cause)...")
            try:
                refute = model.refute_estimate(
                    identified_estimand,
                    estimate,
                    method_name="random_common_cause",
                    show_progress_bar=False
                )
                print(f"Refutation p-value: {refute.refutation_result['p_value']:.4f}")
                print(f"Refutation New Effect: {refute.new_effect:.4f}")
            except Exception as e:
                print(f"[Warning] Refutation failed: {e}")
            
            return estimate.value
        else:
            return 0.0