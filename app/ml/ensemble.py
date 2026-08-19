import numpy as np

from sklearn.preprocessing import StandardScaler

from .models import create_models


def get_model_probabilities(X_train, y_train, X_current):
    """
    Train all models and return their UP probabilities.
    """

    models = create_models()

    probabilities = {}
    predictions = {}

    for model_name, model in models.items():

        if model_name == "Logistic Regression":
            scaler = StandardScaler()

            X_train_model = scaler.fit_transform(X_train)
            X_current_model = scaler.transform(X_current)

        else:
            X_train_model = X_train
            X_current_model = X_current

        model.fit(
            X_train_model,
            y_train
        )

        probability = float(
            model.predict_proba(
                X_current_model
            )[0][1]
        )

        prediction = int(
            model.predict(
                X_current_model
            )[0]
        )

        probabilities[model_name] = probability
        predictions[model_name] = prediction

    return probabilities, predictions


def calculate_ensemble(probabilities):
    """
    Combine model probabilities.

    Random Forest receives the highest weight because
    it currently performs best in our walk-forward test.
    """

    weights = {
        "Random Forest": 0.50,
        "XGBoost": 0.30,
        "Logistic Regression": 0.20,
    }

    weighted_probability = sum(
        probabilities[name] * weights[name]
        for name in weights
    )

    up_probability = weighted_probability
    down_probability = 1.0 - up_probability

    if up_probability >= 0.55:
        direction = "UP"
    elif up_probability <= 0.45:
        direction = "DOWN"
    else:
        direction = "NEUTRAL"

    confidence = max(
        up_probability,
        down_probability
    ) * 100

    # Avoid calling weak predictions BUY/SELL.
    if direction == "UP" and confidence >= 60:
        signal = "BUY"

    elif direction == "DOWN" and confidence >= 60:
        signal = "SELL"

    else:
        signal = "HOLD"

    return {
        "direction": direction,
        "signal": signal,
        "confidence": round(confidence, 2),
        "up_probability": round(
            up_probability * 100,
            2
        ),
        "down_probability": round(
            down_probability * 100,
            2
        ),
    }


def ensemble_prediction(
    X_train,
    y_train,
    X_current
):
    """
    Complete ensemble prediction.
    """

    probabilities, predictions = (
        get_model_probabilities(
            X_train,
            y_train,
            X_current
        )
    )

    result = calculate_ensemble(
        probabilities
    )

    result["model_probabilities"] = {
        name: round(
            probability * 100,
            2
        )
        for name, probability
        in probabilities.items()
    }

    result["model_predictions"] = {
        name: (
            "UP" if prediction == 1
            else "DOWN"
        )
        for name, prediction
        in predictions.items()
    }

    return result