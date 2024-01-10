class Globals:
    SCRIPT_START_TIME = None
    LAST_MESSAGE_ID = None

class WebData:
    CURRENT_BALANCE: float = 0.00
    LIFETIME_BALANCE: float = 0.00
    
class Settings:
    EMAIL: str = ''
    BOT_TOKEN: str = ''
    BOT_CHANNEL: int = 0
    DEBUG: bool = False