from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    media_dir: str = "media"


def load_config() -> Config:
    load_dotenv()

    token = getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Add it to .env or environment variables.")

    return Config(
        bot_token=token,
        media_dir=getenv("MEDIA_DIR", "media"),
    )
