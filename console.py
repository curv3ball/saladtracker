import functools
import datetime
import time
import os
import sys

class SaladNotRunningException(Exception):
    """Exception raised when Salad.exe is not running."""
    def __init__(self, message="Salad.exe must be running, please run Salad before running this program."):
        """
        Initializes the SaladNotRunningException.

        Args:
            message (str): Custom error message (default is a generic message).

        """
        self.message = message
        super().__init__(self.message)

def loggable(func):
    """
    Decorator function for logging the execution of another function.

    Args:
        func (callable): The function to be logged.

    Returns:
        callable: The wrapper function for logging.

    """
    @functools.wraps(func)
    def wrapper(*args: tuple, **kwargs: dict):
        """
        Wrapper function that logs the execution of the decorated function.

        Args:
            *args: Positional arguments for the decorated function.
            **kwargs: Keyword arguments for the decorated function.

        Returns:
            Any: The result of the decorated function.

        """
        # Initialize logging variables
        log_level, log_error = "INFO", None
        start_time = time.time()

        try:
            # Execute the decorated function
            result = func(*args, **kwargs)
        except Exception as function_exception:
            # Handle exceptions and update logging variables
            log_level, log_error = "ERROR", str(function_exception)
            result = None  # Set result to None in case of an error

        try:
            # Get current time and date for log timestamp
            current_time = datetime.datetime.now().strftime("%I:%M%p")
            current_date = datetime.datetime.now().strftime("%m_%d_%Y")

            # Set up log file path
            folder_path = "logs"
            file_path = os.path.join(folder_path, f"{current_date}.txt")

            # Prepare log information in a dictionary
            log_params = {
                'execution_time': time.time() - start_time,
                'result_info': ', '.join(
                    f'{type(value).__name__}={value}' for value in result
                ) if result is not None and log_level != 'ERROR' else '',
                'error_info': log_error,
            }

            # Format the log message for better readability
            log_message = (
                f"[{current_time}][{log_level}] => {func.__name__}("
                f"{', '.join(f'{type(arg).__name__}' for arg in args)}) | "
                f"time: {log_params['execution_time']:.2f}s | "
                f"{log_params['result_info']} {log_params['error_info']}"
            )

            # Ensure the logs folder exists
            os.makedirs(folder_path, exist_ok=True)
            os.makedirs(os.path.join(folder_path, "screenshots"), exist_ok=True)

            # Write the log message to the log file
            with open(file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(f"{log_message}\n")

        except Exception as log_exception:
            with open(file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(f"Logging Error => {result} | {log_exception}\n")

        # Return the result or None if an error occurred
        return result

    return wrapper

def log(msg: str, clear: bool = False):
    """
    Prints a log message and optionally clears the console.

    Args:
        msg (str): The log message to be printed.
        clear (bool): Whether to clear the console before printing (default is False).

    """
    if clear:
        cls()

    print(msg)

def cls():
    """Clears the console buffer."""
    os.system('cls' if os.name == 'nt' else 'clear')
