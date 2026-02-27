import time
from typing import List, Optional
from app.model import IntervalModel, IntervalProgressModel


class Timer:
    def __init__(self, intervals: List[IntervalModel]):
        """
        Initialize the timer with a list of intervals.
        """
        self._intervals = intervals
        self._start_time = None
        self._rounds_completed = 0  # total completed rounds
        self._is_running = False

    def set_intervak(self, intervals: List[IntervalModel]):
        self._intervals = intervals

    def is_running(self) -> bool:
        return self._is_running

    def start(self):
        """Start the timer."""
        self._start_time = time.time()
        self._is_running = True
        self._rounds_completed = 0

    def stop(self):
        """Stop the timer."""
        self._is_running = False
        self._start_time = None

    def current_interval(self) -> Optional[IntervalProgressModel]:
        """
        Return an IntervalProgressModel for the current interval.
        Loops through intervals repeatedly, counting rounds.
        """

        if self._start_time is None or self._intervals is None:
            return IntervalProgressModel(
                is_running=self._is_running,
            )

        total_elapsed = time.time() - self._start_time

        if len(self._intervals) == 0:
            return IntervalProgressModel(
                interval=IntervalModel(name="Enldess", seconds=round(total_elapsed)),
                time_spent=total_elapsed,
                total_time_spent=total_elapsed,
                is_running=self._is_running,
            )

        interval_duration = sum(interval.seconds for interval in self._intervals)

        # Determine how many full rounds have passed
        rounds_completed = int(total_elapsed // interval_duration)
        self._rounds_completed = rounds_completed + 1  # human-readable 1-based

        # Determine time within current round
        time_in_round = total_elapsed % interval_duration

        cumulative = 0
        for interval in self._intervals:
            if time_in_round < cumulative + interval.seconds:
                time_in_interval = time_in_round - cumulative
                time_remaining = interval.seconds - time_in_interval
                return IntervalProgressModel(
                    interval=interval,
                    time_spent=time_in_interval,
                    time_remaining=time_remaining,
                    total_time_spent=total_elapsed,
                    round_number=self._rounds_completed,  # include round info
                    is_running=self._is_running,
                )
            cumulative += interval.seconds

        # fallback, should never reach here
        return IntervalProgressModel(
            time_spent=total_elapsed,
            total_time_spent=total_elapsed,
            is_running=self._is_running,
        )
