from dataclasses import dataclass, field
from typing import List

# pylint don't support @dataclass
# pylint: disable=no-member, unsupported-assignment-operation,unsupported-membership-test, unsubscriptable-object


@dataclass
class StateMachine:
    __handlers: dict = field(default_factory=lambda: {})
    __start_state: str = None
    __end_states: List[str] = field(default_factory=lambda: [])

    def add_state(self, name: str, handler: any, end_state: bool = False):
        self.__handlers[name] = handler
        if end_state:
            self.__end_states.append(name)

    def set_start(self, name: str) -> None:
        self.__start_state = name

    def run(self) -> None:
        try:
            handler = self.__handlers[self.__start_state]
        except Exception as exception:
            raise Exception(
                "must call .set_start() before .run()") from exception
        if not self.__end_states:
            raise Exception("at least one state must be an end_state")

        while True:
            new_state = handler()
            if new_state in self.__end_states:
                break
            handler = self.__handlers[new_state]
