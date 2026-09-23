from app.ml.train import train_all
from app.services.live_simulator import get_simulator, reset_simulator


def test_live_simulator_tick():
    train_all(force=True)
    reset_simulator("EXC001")
    sim = get_simulator("EXC001")
    payload = sim.tick()

    assert payload["machine_id"] == "EXC001"
    assert payload["environment"] is not None
    assert payload["environment"]["current"]["co2_ppm"] > 0
    assert payload["engine"] in ("ml", "rules")
