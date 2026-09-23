"""Real-time engine — replays sensor history with ML scoring (primary)."""

import logging

from app.ml.train import models_ready
from app.services import ergonomics as ergo_svc
from app.services import environment as env_svc
from app.services.live_simulator_rules import MachineLiveSimulator
from app.services.machines import get_machine
from app.services.replay_engine import get_replay_engine, reset_replay_engine

logger = logging.getLogger(__name__)

_engines: dict = {}


def _operator_for_machine(machine_id: str) -> str:
    try:
        ergo = ergo_svc.get_ergonomics_df(machine_id)
        if not ergo.empty:
            return str(ergo.iloc[-1]["Operator ID"])
        env = env_svc.get_environment_df(machine_id)
        if not env.empty:
            return str(env.iloc[-1]["Operator ID"])
    except FileNotFoundError:
        pass
    return "OP1001"


def get_simulator(machine_id: str):
    machine = get_machine(machine_id)
    if not machine:
        raise ValueError(f"Unknown machine: {machine_id}")

    if machine_id not in _engines:
        operator_id = _operator_for_machine(machine_id)
        has_ergo = machine["capabilities"]["ergonomics"]
        if models_ready():
            logger.info("Replay+ML engine for %s", machine_id)
            _engines[machine_id] = get_replay_engine(machine_id, operator_id, has_ergo)
        else:
            logger.warning("ML models missing — rule fallback for %s", machine_id)
            _engines[machine_id] = MachineLiveSimulator(machine_id, operator_id, has_ergo)

    return _engines[machine_id]


def reset_simulator(machine_id: str) -> None:
    _engines.pop(machine_id, None)
    reset_replay_engine(machine_id)


def engine_mode() -> str:
    return "ml" if models_ready() else "rules"
