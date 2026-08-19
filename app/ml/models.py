from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


def create_random_forest():
    return RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=5,
        random_state=42,
        class_weight="balanced"
    )


def create_xgboost():
    return XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=4
    )


def create_logistic_regression():
    return LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    )


def create_models():
    return {
        "Random Forest": create_random_forest(),
        "XGBoost": create_xgboost(),
        "Logistic Regression": create_logistic_regression()
    }