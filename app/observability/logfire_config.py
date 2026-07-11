import logfire
from app.config import settings

logfire.configure(
    token=settings.LOGFIRE_TOKEN,
    service_name="dsa-sensei"
)