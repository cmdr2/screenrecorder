"""
History module for managing video editing operations with Apply/Undo functionality.
This module provides a shared history system that can be used by all toolbar tools.
"""

from tkinter_videoplayer.events import EventDispatcher


class EditHistory(EventDispatcher):
    """
    Manages the history of edits for undo functionality.
    """

    def __init__(self):
        super().__init__()

        self.history = []
        self.current_index = -1

    def add(self, value):
        # Remove any history after current index (if user undid and then made new changes)
        self.history = self.history[: self.current_index + 1]

        # Add new entry
        self.history.append(value)
        self.current_index += 1

        # Dispatch events
        self.dispatch_event("change", new_value=value)

    def can_undo(self):
        return self.current_index > 0

    def undo(self):
        if self.can_undo():
            self.current_index -= 1
            previous = self.history[self.current_index]

            # Dispatch events
            self.dispatch_event("change", new_value=previous)

            return True
        return False

    def get_current(self):
        """Get the currently active entry."""
        return self.history[self.current_index]
