"""Story data class entity."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Story:
    id: str
    description: str
    options: list[StoryOption] = field(default_factory=list)
    start_point: bool = field(default=False)
    affect_status: dict[str, int] = field(default_factory=dict)
    goto: str | None = field(default=None)
    next_event: str | None = field(default=None)

    def __post_init__(self):
        if sum([self.goto is not None, bool(self.options), self.next_event is not None]) > 1:
            msg = "You must choose and set only one among goto, options, or next_event."
            raise ValueError(msg)

        if self.options:
            for idx in range(len(self.options)):
                option = self.options[idx]
                if isinstance(option, StoryOption):
                    continue
                if isinstance(option, dict):
                    try:
                        self.options[idx] = StoryOption(**option)
                    except:
                        breakpoint()
                else:
                    raise TypeError(type(option))


@dataclass
class StoryOption:
    description: str
    goto: str
    next_description: str = field(default="")
    visible: bool = field(default=True)
    status_condition: dict[str, int] = field(default_factory=dict)
