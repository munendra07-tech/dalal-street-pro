import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

from sklearn.preprocessing import StandardScaler

from .features import prepare_training_data
from .models import create_models


def walk_forward_backtest(
    df,
    train_size=600,
    test_size=100,
    step_size=100,
):
    """
    Walk-forward time-series backtesting.

    Example:

    Train: rows 0-599
    Test:  rows 600-699

    Train: rows 0-699
    Test:  rows 700-799

    Train: rows 0-799
    Test:  rows 800-899
    """

    X, y, clean_df = prepare_training_data(df)

    if len(X) < train_size + test_size:
        raise ValueError(
            f"Not enough data. Need at least "
            f"{train_size + test_size} rows, "
            f"but only {len(X)} available."
        )

    models = create_models()

    results = {}

    for model_name in models:

        actual_all = []
        predicted_all = []
        probability_all = []

        start = train_size

        while start < len(X):

            end = min(
                start + test_size,
                len(X)
            )

            X_train = X.iloc[:start]
            y_train = y.iloc[:start]

            X_test = X.iloc[start:end]
            y_test = y.iloc[start:end]

            if len(X_test) == 0:
                break

            model = create_models()[model_name]

            # Logistic Regression benefits from scaling.
            # Tree models do not require scaling.
            if model_name == "Logistic Regression":

                scaler = StandardScaler()

                X_train_model = scaler.fit_transform(
                    X_train
                )

                X_test_model = scaler.transform(
                    X_test
                )

            else:

                X_train_model = X_train
                X_test_model = X_test

            model.fit(
                X_train_model,
                y_train
            )

            predictions = model.predict(
                X_test_model
            )

            probabilities = model.predict_proba(
                X_test_model
            )[:, 1]

            actual_all.extend(
                y_test.tolist()
            )

            predicted_all.extend(
                predictions.tolist()
            )

            probability_all.extend(
                probabilities.tolist()
            )

            start += step_size

        actual = np.array(actual_all)
        predicted = np.array(predicted_all)
        probabilities = np.array(probability_all)

        metrics = {
            "accuracy": accuracy_score(
                actual,
                predicted
            ),
            "precision": precision_score(
                actual,
                predicted,
                zero_division=0
            ),
            "recall": recall_score(
                actual,
                predicted,
                zero_division=0
            ),
            "f1": f1_score(
                actual,
                predicted,
                zero_division=0
            ),
            "samples": len(actual),
        }

        # ROC-AUC requires both classes to exist.
        if len(np.unique(actual)) > 1:
            metrics["roc_auc"] = roc_auc_score(
                actual,
                probabilities
            )
        else:
            metrics["roc_auc"] = None

        results[model_name] = metrics

    return results


def print_backtest_results(results):

    print("\n" + "=" * 70)
    print("AI MODEL WALK-FORWARD BACKTEST")
    print("=" * 70)

    for model_name, metrics in results.items():

        print(f"\n{model_name}")

        print(
            f"  Accuracy : {metrics['accuracy'] * 100:.2f}%"
        )

        print(
            f"  Precision: {metrics['precision'] * 100:.2f}%"
        )

        print(
            f"  Recall   : {metrics['recall'] * 100:.2f}%"
        )

        print(
            f"  F1 Score : {metrics['f1'] * 100:.2f}%"
        )

        if metrics["roc_auc"] is not None:

            print(
                f"  ROC-AUC  : {metrics['roc_auc']:.4f}"
            )

        print(
            f"  Samples  : {metrics['samples']}"
        )

    print("\n" + "=" * 70)


if __name__ == "__main__":

    import yfinance as yf

    ticker = "RELIANCE.NS"

    print(
        f"Downloading historical data for {ticker}..."
    )

    df = yf.Ticker(ticker).history(
        period="5y",
        auto_adjust=False
    )

    print(
        f"Downloaded {len(df)} rows."
    )

    results = walk_forward_backtest(
        df,
        train_size=600,
        test_size=100,
        step_size=100,
    )

    print_backtest_results(results)