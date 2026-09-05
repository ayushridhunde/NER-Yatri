import pytest
from ai.inference.inference import landslide_engine

def test_inference_engine_prediction():
    """Verify that the AI model produces valid prediction schema and calibrated window."""
    sample_input = {
        "rainfall": 160.0,
        "rainfall_24h": 160.0,
        "slope": 38.0,
        "elevation": 1400.0,
        "soil_moisture": 0.88,
        "soil_type": 0,
        "geology": 0,
        "historical_landslide_density": 0.6
    }
    pred = landslide_engine.predict(sample_input)

    assert "risk_probability" in pred
    assert "risk_level" in pred
    assert "prediction_window" in pred
    assert "confidence" in pred
    assert "contributing_factors" in pred

    # Check value bounds
    assert 0.0 <= pred["risk_probability"] <= 1.0
    assert pred["risk_level"] in ["LOW", "MEDIUM", "HIGH", "VERY HIGH"]
    assert pred["prediction_window"] == "6–24 hours"
    assert 0.70 <= pred["confidence"] <= 0.99
    assert len(pred["contributing_factors"]) > 0

def test_inference_engine_factor_explainability():
    """Verify that heavy rainfall and steep slopes produce explicit factors."""
    high_hazard = {
        "rainfall_24h": 180.0,
        "slope": 42.0,
        "soil_moisture": 0.90
    }
    factors = landslide_engine.explain_factors(high_hazard)
    factor_texts = " ".join([f["factor"] for f in factors])

    assert "rainfall" in factor_texts.lower()
    assert "slope" in factor_texts.lower()

def test_inference_engine_low_risk():
    """Verify that gentle slopes and zero rain return LOW risk."""
    gentle = {
        "rainfall_24h": 0.0,
        "slope": 5.0,
        "elevation": 80.0,
        "soil_moisture": 0.25,
        "historical_landslide_density": 0.0
    }
    pred = landslide_engine.predict(gentle)
    assert pred["risk_level"] == "LOW"
    assert pred["risk_probability"] < 0.30
