class Globals:
    SCRIPT_START_TIME = None
    LAST_MESSAGE_ID = None

class WebData:
    CURRENT_BALANCE: float = 0.00

class Settings:
    """Class for storing and managing settings."""
    EMAIL       : str = ''
    BOT_TOKEN   : str = ''
    DEBUG       : bool = False