import logging

class Setup:

    def log_unhandled_exception(exc_type, exc_value, exc_traceback):
        # Log the unhandled exception
        logger.critical(
            "Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback)
        )
