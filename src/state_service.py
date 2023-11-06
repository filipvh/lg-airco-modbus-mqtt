from loguru import logger

from event_hook import EventHook
from models.state import State


class StateService:

    def __init__(self):
        self._state = State()

        self.state_changed = EventHook[State]()

    def merge_in_state(self, state: State, skip_emit: bool = False):
        # Make a copy of the current state to compare later
        old_state_data = self._state.model_dump()
        # Dictionary to hold changes
        changes = {}

        # Merge new state into the current state
        for name, value in state.model_dump().items():
            if value is not None:  # Only merge values that are not None
                setattr(self._state, name, value)
                # If the value is different from the old state, record the change
                if old_state_data[name] != value:
                    changes[name] = value

        # If there are any changes, create a state with only those changes
        if changes and not skip_emit:
            delta_state = State(**changes)
            self._process_changes(delta_state)

    def _process_changes(self, delta_state: State):
        logger.debug(f"State  | Changed state: {delta_state}")
        self.state_changed.fire(delta_state)

    def get_state(self) -> State:
        return self._state
