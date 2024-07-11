import logging
import zoneinfo
from datetime import datetime, timedelta


class Dates:
    """A class for date related functions in EOD2"""

    def __init__(self,
                 logger: logging.Logger,
                 timezone: zoneinfo.ZoneInfo, tz_local: zoneinfo.ZoneInfo,
                 last_update: str):
        self.TIME_ZONE = timezone
        self.logger = logger
        self.tz_local = tz_local

        today = datetime.now(self.TIME_ZONE)
        self.today = datetime.combine(today, datetime.min.time())

        dt = datetime.fromisoformat(last_update).astimezone(self.TIME_ZONE)

        self.dt = self.lastUpdate = dt

        self.pandasDt = self.dt.strftime("%Y-%m-%d")

    def next_date(self):
        """Set the next trading date and return True.
        If its a future date, return False"""

        curTime = datetime.now(self.TIME_ZONE)
        self.dt = self.dt + timedelta(1)

        if self.dt > curTime:
            self.logger.info("All Up To Date")
            return False

        if self.dt.day == curTime.day and curTime.hour < 18:
            # Display the users local time
            local_time = curTime.replace(hour=19, minute=0).astimezone(self.tz_local)

            t_str = local_time.strftime("%I:%M%p")  # 07:00PM
            self.logger.info(
                f"All Up To Date. Check again after {t_str} for today's EOD data"
            )
            return False

        self.pandasDt = self.dt.strftime("%Y-%m-%d")
        return True
