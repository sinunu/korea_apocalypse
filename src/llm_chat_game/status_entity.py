"""Status class entity."""

from __future__ import annotations


class Status:
    """Status entity class."""
    def __init__(self, name: str, inital_val: int = 3, max_val: int = 4, min_val: int = 0) -> None:
        self._name = name
        self._val = inital_val
        self._max = max_val
        self._min = min_val

    @property
    def name(self) -> str:
        return self._name

    @property
    def val(self) -> int:
        return self._val

    @property
    def max(self) -> int:
        return self._max

    @property
    def min(self) -> int:
        return self._min

    def add(self, val=1) -> None:
        self._val += val
        if self._val > self._max:
            self._val = self._max
        elif self._val < self._min:
            self._val = self._min

    def subtract(self, val=1) -> None:
        self._val -= val
        if self._val > self._max:
            self._val = self._max
        elif self._val < self._min:
            self._val = self._min

    def set_to_max(self) -> None:
        self._val = self._max

    def set_to_min(self) -> None:
        self._val = self._min



class StatusManager:
    """Class which manages health, mental and money status."""

    LIFE_STATUS: list[str] = ["health", "mental"]

    def __init__(self):
        self._statuses: dict[str, Status] = {
            "health" : Status(name="health"),
            "mental" : Status(name="mental"),
            "money" : Status(name="money"),
        }
        
    def add_status(self, status_name: str, val: int = 1) -> None:
        if status_name not in self._statuses:
            msg = f"{status_name} doesn't exist."
            raise ValueError(msg)

        self._statuses[status_name].add(val)

    def subtract_status(self, status_name: str, val: int = 1) -> None:
        if status_name not in self._statuses:
            msg = f"{status_name} doesn't exist."
            raise ValueError(msg)

        self._statuses[status_name].subtract(val)
    
    def is_die(self) -> bool:
        for status_name in self.LIFE_STATUS:
            if self._statuses[status_name].val == self._statuses[status_name].min:
                return True
        return False

    def __str__(self):
        return f"현재 상태 : 체력 {self._statuses['health'].val} / 정신 {self._statuses['mental'].val} / 돈 {self._statuses['money'].val}"
