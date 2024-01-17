class Globals:
    SCRIPT_START_TIME = None
    LAST_MESSAGE_ID = None
    SCRIPT_UP_TIME = None
    FILE_SENT = False

class LogData:
    CURRENT_BALANCE: float = 0.00

class Settings:
    EMAIL: str = ''
    BOT_TOKEN: str = ''
    BOT_CHANNEL: int = 0
    DEBUG: bool = False