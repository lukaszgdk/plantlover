import json
import os
import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..schemas import AppConfig, AppConfigPublic

router = APIRouter(prefix="/config", tags=["config"])

CONFIG_PATH = Path(os.environ.get("CONFIG_PATH", "/data/config.json"))


def _load() -> AppConfig:
    if CONFIG_PATH.exists():
        try:
            return AppConfig(**json.loads(CONFIG_PATH.read_text()))
        except Exception:
            pass
    return AppConfig()


def _save(cfg: AppConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(cfg.model_dump_json(indent=2))
    _apply_env(cfg)


def _apply_env(cfg: AppConfig) -> None:
    """Push config values into the current process environment so the rest of
    the app sees them without a restart. A full restart is still needed for the
    Discord bot service."""
    if cfg.plantnet_api_key:
        os.environ["PLANTNET_API_KEY"] = cfg.plantnet_api_key
    if cfg.discord_bot_token:
        os.environ["DISCORD_BOT_TOKEN"] = cfg.discord_bot_token
    if cfg.discord_channel_id:
        os.environ["DISCORD_CHANNEL_ID"] = cfg.discord_channel_id


def load_config_into_env() -> None:
    """Called at startup to apply stored config to env."""
    cfg = _load()
    _apply_env(cfg)


@router.get("/status")
def setup_status():
    cfg = _load()
    return {"completed": cfg.setup_completed}


@router.get("", response_model=AppConfigPublic)
def get_config():
    cfg = _load()
    return AppConfigPublic(
        setup_completed=cfg.setup_completed,
        plantnet_api_key_set=bool(cfg.plantnet_api_key or os.environ.get("PLANTNET_API_KEY")),
        discord_bot_token_set=bool(cfg.discord_bot_token or os.environ.get("DISCORD_BOT_TOKEN")),
        discord_channel_id=cfg.discord_channel_id or os.environ.get("DISCORD_CHANNEL_ID"),
    )


@router.put("")
def save_config(payload: AppConfig):
    cfg = _load()

    # Only overwrite non-None values so partial updates don't wipe fields
    if payload.plantnet_api_key is not None:
        cfg.plantnet_api_key = payload.plantnet_api_key or None
    if payload.discord_bot_token is not None:
        cfg.discord_bot_token = payload.discord_bot_token or None
    if payload.discord_channel_id is not None:
        cfg.discord_channel_id = payload.discord_channel_id or None
    if payload.setup_completed:
        cfg.setup_completed = True

    _save(cfg)

    # Restart discord-bot service if token/channel changed (fire-and-forget)
    if payload.discord_bot_token or payload.discord_channel_id:
        try:
            subprocess.Popen(
                ["systemctl", "restart", "discord-bot"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    return {"ok": True}


@router.post("/complete-setup")
def complete_setup():
    cfg = _load()
    cfg.setup_completed = True
    _save(cfg)
    return {"ok": True}
