from fastapi import APIRouter, HTTPException

from app.ml.predict_service import run_ai_prediction, PredictionError


router = APIRouter(
    prefix="/prediction/ai",
    tags=["AI Predictions"]
)


@router.get("/{ticker}")
def ai_prediction(ticker: str):
    try:
        return run_ai_prediction(ticker)
    except PredictionError as e:
        # 404 for "no data", 400 for "not enough data" -- both are client-facing,
        # expected conditions, not server errors.
        status = 404 if "No market data" in str(e) else 400
        raise HTTPException(status_code=status, detail=str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"AI prediction error: {str(e)}")
