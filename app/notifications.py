from abc import ABC, abstractmethod


class Notification(ABC):
    """Interface for notification strategies."""

    @abstractmethod
    def send_message(self, message: str):
        """Send a notification with the given message."""
        pass


class ConsoleNotification(Notification):
    """Notification strategy that prints messages to the console."""

    def send_message(self, message: str):
        print(f"Notification: {message}")
