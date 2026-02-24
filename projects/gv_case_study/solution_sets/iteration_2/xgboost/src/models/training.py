from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import mlflow
import pandas as pd
import seaborn as sns
import xgboost as xgb
from src.models.metrics import calculate_mean_ndcg, calculate_ndcg

@mlflow.trace
def train_ranker(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    params: Dict[str, Any],
    tracking_uri: str,
    experiment_name: str,
    train_groups: Optional[List[int]] = None,
    test_groups: Optional[List[int]] = None,
    industry_names: Optional[List[str]] = None,
    run_name: Optional[str] = None,
) -> Tuple[xgb.XGBRanker, Dict[str, float]]:
    """
    Train XGBRanker with MLflow tracking.

    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        params: XGBoost hyperparameters
        tracking_uri: MLflow tracking URI
        experiment_name: MLflow experiment name
        train_groups: List of group sizes for training data (per-industry counts)
        test_groups: List of group sizes for test data (per-industry counts)
        industry_names: List of industry names corresponding to groups
        run_name: Optional run name for MLflow

    Returns:
        Tuple of (trained ranker, metrics dict)
    """
    mlflow.enable_system_metrics_logging()
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    # Enable autologging for traces and system metrics
    mlflow.xgboost.autolog(log_input_examples=True, log_model_signatures=True)

    ranker = xgb.XGBRanker(**params)
    metric_name = params.get("eval_metric", "ndcg")

    # Use provided groups or default to single group
    train_group = train_groups if train_groups is not None else [len(X_train)]
    test_group = test_groups if test_groups is not None else [len(X_test)]

    with mlflow.start_run(run_name=run_name):
        mlflow.log_params(params)
        mlflow.log_param("train_rows", len(X_train))
        mlflow.log_param("test_rows", len(X_test))
        mlflow.log_param("features", len(X_train.columns))
        mlflow.log_param("train_groups", str(train_group))
        mlflow.log_param("test_groups", str(test_group))
        mlflow.log_param("num_cohorts", len(train_group))

        # Log label distribution
        fig_labels, ax_labels = plt.subplots(figsize=(10, 6))
        sns.histplot(data=y_train, kde=False, ax=ax_labels)
        ax_labels.set_title("Training Label Distribution")
        ax_labels.set_xlabel("Relevance Grade")
        ax_labels.set_ylabel("Count")
        mlflow.log_figure(fig_labels, "label_distribution.png")
        plt.close(fig_labels)

        ranker.fit(
            X_train,
            y_train,
            group=train_group,
            eval_set=[(X_train, y_train), (X_test, y_test)],
            eval_group=[train_group, test_group],
            verbose=False,
        )
        
        # Log feature importance
        importance = ranker.feature_importances_
        feature_names = X_train.columns
        feat_imp = pd.DataFrame({'feature': feature_names, 'importance': importance})
        feat_imp = feat_imp.sort_values('importance', ascending=False).head(20)
        
        fig_imp, ax_imp = plt.subplots(figsize=(10, 8))
        sns.barplot(data=feat_imp, x='importance', y='feature', ax=ax_imp)
        ax_imp.set_title("Top 20 Feature Importance")
        mlflow.log_figure(fig_imp, "feature_importance.png")
        plt.close(fig_imp)
        
        # Calculate metrics
        train_scores = ranker.predict(X_train)
        test_scores = ranker.predict(X_test)

        # Log model with signature
        from mlflow.models import infer_signature
        signature = infer_signature(X_train, train_scores)
        mlflow.xgboost.log_model(ranker, "model", signature=signature)

        # Calculate per-group NDCG scores
        train_ndcg_per_group = []
        test_ndcg_per_group = []
        
        train_start = 0
        test_start = 0
        
        for idx, (train_size, test_size) in enumerate(zip(train_group, test_group)):
            # Calculate NDCG for this group
            train_end = train_start + train_size
            test_end = test_start + test_size
            
            train_group_ndcg = calculate_ndcg(
                y_train.tolist()[train_start:train_end],
                train_scores.tolist()[train_start:train_end],
                metric_name
            )
            test_group_ndcg = calculate_ndcg(
                y_test.tolist()[test_start:test_end],
                test_scores.tolist()[test_start:test_end],
                metric_name
            )
            
            train_ndcg_per_group.append(train_group_ndcg)
            test_ndcg_per_group.append(test_group_ndcg)
            
            train_start = train_end
            test_start = test_end
        
        # Calculate mean NDCG
        train_ndcg = sum(train_ndcg_per_group) / len(train_ndcg_per_group) if train_ndcg_per_group else 0.0
        test_ndcg = sum(test_ndcg_per_group) / len(test_ndcg_per_group) if test_ndcg_per_group else 0.0

        mlflow.log_metric(f"train_{metric_name}".replace('@', '-'), train_ndcg)
        mlflow.log_metric(f"test_{metric_name}".replace('@', '-'), test_ndcg)
        
        # Print per-industry scores
        print(f"\n=== Per-Industry {metric_name.upper()} Scores ===")
        for idx, (train_score, test_score) in enumerate(zip(train_ndcg_per_group, test_ndcg_per_group)):
            industry_name = industry_names[idx] if industry_names and idx < len(industry_names) else f"Group {idx+1}"
            print(f"{industry_name}:")
            print(f"  Train: {train_score:.4f} | Test: {test_score:.4f}")
        
        print(f"\n=== Mean {metric_name.upper()} ===")
        print(f"Train {metric_name}: {train_ndcg:.4f}")
        print(f"Test {metric_name}: {test_ndcg:.4f}")

    return ranker, {f"train_{metric_name}": train_ndcg, f"test_{metric_name}": test_ndcg}
