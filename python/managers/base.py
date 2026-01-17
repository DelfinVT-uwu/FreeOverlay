"""
Base Manager Class.

Defines the interface that all managers should implement.
Ensures consistent lifecycle and error handling across all managers.
"""

from abc import ABC, abstractmethod
from core.logger import get_logger

logger = get_logger("Manager")


class Manager(ABC):
    """
    Abstract base class for all application managers.

    A Manager is a component that:
    - Has a clear single responsibility
    - Can be started and stopped
    - Can handle errors gracefully
    - Is testable in isolation

    All managers should inherit from this class and implement:
    - start(): Initialize manager resources
    - stop(): Clean up manager resources
    - on_error(): Handle errors that occur in the manager

    Example:
        class MediaManager(Manager):
            def start(self):
                self._start_polling_thread()

            def stop(self):
                self._running = False

            def on_error(self, error):
                logger.error(f"Media error: {error}")
    """

    def __init__(self, name: str = None):
        """
        Initialize manager.

        Args:
            name: Manager identifier (defaults to class name)
        """
        self.name = name or self.__class__.__name__
        self._running = False
        logger.debug(f"Manager initialized: {self.name}")

    @abstractmethod
    def start(self) -> None:
        """
        Start the manager.

        Initialize any resources, threads, or background tasks.
        Should be idempotent - can be called multiple times safely.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the manager.

        Clean up resources, stop threads, close connections.
        Should be idempotent - can be called multiple times safely.
        """
        pass

    @abstractmethod
    def on_error(self, error: Exception) -> None:
        """
        Handle an error that occurred in the manager.

        Args:
            error: The exception that occurred

        This should not raise, but log and handle gracefully.
        """
        pass

    def is_running(self) -> bool:
        """Check if manager is currently running."""
        return self._running

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False
