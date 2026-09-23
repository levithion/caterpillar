from app.ml.train import models_ready, train_all
from app.services.live_simulator import engine_mode, get_simulator, reset_simulator


def test_train_models():
    meta = train_all(force=True)
    assert models_ready()
    assert meta["ergonomics_samples"] > 100
    assert meta["environment_samples"] > 100


def test_ml_live_tick():
    train_all(force=True)
    reset_simulator("EXC001")
    sim = get_simulator("EXC001")
    payload = sim.tick()

    assert payload["engine"] == "ml"
    assert payload["environment"] is not None
    assert payload["environment"]["current"]["prediction_source"] == "ml"
    if payload["ergonomics"]:
        assert "shock_probability" in payload["ergonomics"]["current"]
        assert "anomaly_score" in payload["ergonomics"]["current"]
    assert "replay_index" in payload


def test_engine_mode():
    train_all(force=True)
    assert engine_mode() == "ml"
