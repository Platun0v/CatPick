import threading
import datetime
from time import sleep
import warnings


class Timer(threading.Thread):
    """Class to run function in some moments in other thread

    :param target: Function to run
    :type target: function

    :param args: Tuple of arguments for function
    :type args: tuple

    :param kwargs: Dictionary of key word arguments for function
    :type kwargs: dict

    """

    DAY = 60 * 60 * 24

    def __init__(self, target, args=(), kwargs=None):
        threading.Thread.__init__(self)
        self._target = target
        self._args = args

        self._kwargs = kwargs
        if kwargs is None:
            self._kwargs = {}

        self._times = None
        self._selected_variant = {
            'everyday': False,
            'every_time_step': False,
            'every_week': False,
        }

    def _reset_selected_variant(self):
        """Sets selected variant to False"""
        for key, elem in self._selected_variant.items():
            self._selected_variant[key] = False

    def _get_selected_variant(self):
        """Returns the name of selected variant"""
        for key, elem in self._selected_variant.items():
            if elem:
                return f"_run_{key}"

    def _call_target(self):
        """Calls target function with args and kwargs"""
        self._target(*self._args, **self._kwargs)

    def _choose_time_to_start(self, times):
        min_diff = 60 * 60 * 24 + 1
        it = -1
        for i, time in enumerate(times):
            time_diff = self._time_diff(time, self._time_now())
            if time_diff >= 0:
                if min_diff > time_diff:
                    min_diff = time_diff
                    it = i

        return it

    def _next_weekday_to_call(self, weekdays):
        today = self._get_weekday()
        it = today + 1
        for weekday in weekdays[today + 1:]:
            if weekday:
                break
            it += 1

        if it == 7:
            it = 0
            for weekday in weekdays[:today + 1]:
                if weekday:
                    break
                it += 1

        return it

    def _days_to_sleep(self, weekday):
        time_to_sleep = 0

        today = self._get_weekday()
        if today <= weekday:
            time_to_sleep += self.DAY * (6 - today) \
                             + self.DAY * weekday
        else:
            time_to_sleep += self.DAY * (weekday - today - 1)

        return time_to_sleep

    def run(self):
        if self._times is None:
            raise ValueError('You must choose when to call function before running')
        getattr(self, self._get_selected_variant())()

    @staticmethod
    def _time_now():
        """Returns now time in datetime.time"""
        return datetime.datetime.now().time()

    @staticmethod
    def _time_diff(a, b):
        """Finds diff between two datetime.time"""
        a_seconds = a.hour * 60 * 60 + a.minute * 60 + a.second
        b_seconds = b.hour * 60 * 60 + b.minute * 60 + b.second

        return a_seconds - b_seconds

    @staticmethod
    def _check_time_moments(times):
        for time in times:
            if not isinstance(time, datetime.time):
                raise TypeError('Time moments must be datetime.time')

    @staticmethod
    def _check_weekdays(weekdays):
        if len(weekdays) != 7:
            raise ValueError('weekdays must be have length 7')
        if not any(weekdays):
            raise ValueError('You must select at least 1 day')
        if all(weekdays):
            warnings.warn('if you choose all weekdays, it is better to use Timer.call_everyday')

    @staticmethod
    def _check_time_step(hour, minute, second, day):
        if not 0 <= hour < 24:
            raise ValueError('hour must be in 0..23', hour)
        if not 0 <= minute < 60:
            raise ValueError('minute must be in 0..59', minute)
        if not 0 <= second < 60:
            raise ValueError('second must be in 0..59', second)
        if not 0 <= day:
            raise ValueError('day must be positive', day)

    @staticmethod
    def _get_weekday():
        return datetime.datetime.now().weekday()

    def call_everyday(self, times):
        """
        Sets to call function everyday in given moments

        :param times: Tuple of datetime.time when to call function
        :type times: tuple
        :return:
        """
        self._check_time_moments(times)

        self._times = sorted(times)
        self._reset_selected_variant()
        self._selected_variant['everyday'] = True

    def _run_everyday(self):
        it = self._choose_time_to_start(self._times)

        tomorrow = False
        if it == -1:
            tomorrow = True
            it = 0

        # Main loop
        while True:
            if tomorrow:
                time_to_sleep = self._time_diff(datetime.time(23, 59, 59),
                                                self._time_now()) \
                                + self._time_diff(self._times[it],
                                                  datetime.time(0, 0, 0))
                tomorrow = False
            else:
                time_to_sleep = self._time_diff(self._times[it],
                                                self._time_now())

            sleep(time_to_sleep)
            self._call_target()

            it += 1
            if it == len(self._times):
                it = 0
                tomorrow = True

    def call_every_time_step(self, hour, minute=0, second=0, day=0):
        """
        Sets to call function every time step

        :param hour: Hours in range from 0 to 23
        :type hour: int

        :param minute: Minutes in range from 0 to 59
        :type minute: int

        :param second: Seconds in range from 0 to 59
        :type second: int

        :param day: Days
        :type day: int

        :return:
        """
        self._check_time_step(hour, minute, second, day)

        self._times = day * 24 * 60 * 60 + hour * 60 * 60 + minute * 60 + second
        self._reset_selected_variant()
        self._selected_variant['every_time_step'] = True

    def _run_every_time_step(self):
        # Main loop
        while True:
            self._call_target()
            sleep(self._times)

    def call_every_week(self, weekdays, times):
        """
        Sets to call function every week in given weekdays and in given time moments

        :param weekdays: Tuple of length 7 with 1 and 0 corresponding to the days of the week when to call the function
        :type weekdays: tuple

        :param times: Tuple of datetime.time when to call function
        :type times: tuple

        :return:
        """
        self._check_time_moments(times)
        self._check_weekdays(weekdays)

        self._times = {'weekdays': weekdays,
                       'times': sorted(times)}
        self._reset_selected_variant()
        self._selected_variant['every_week'] = True

    def _run_every_week(self):
        weekdays = self._times['weekdays']
        times = self._times['times']
        today = self._get_weekday()

        it_time = -1  # Next time to call function
        it_day = self._next_weekday_to_call(weekdays)  # Next day to call function

        if weekdays[today]:
            it_time = self._choose_time_to_start(times)
            if it_time == -1:
                it_day = self._next_weekday_to_call(weekdays)
                it_time = 0

        while True:
            today = self._get_weekday()
            if it_day != today:
                time_to_sleep = self._time_diff(datetime.time(23, 59, 59),
                                                self._time_now()) \
                                + self._time_diff(self._times[it_time],
                                                  datetime.time(0, 0, 0)) \
                                + self._days_to_sleep(it_day)
            else:
                time_to_sleep = self._time_diff(self._times[it_day],
                                                self._time_now())

            sleep(time_to_sleep)
            self._call_target()

            it_time += 1
            if it_time == len(self._times):
                it_time = 0
                it_day = self._next_weekday_to_call(weekdays)
