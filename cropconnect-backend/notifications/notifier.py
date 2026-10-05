"""Notification interface with a deliberately simple console implementation."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class Notifier:
    def send_notification(self, title: str, message: str, event: dict) -> None:
        raise NotImplementedError


class ConsoleNotifier(Notifier):
    def send_notification(self, title: str, message: str, event: dict) -> None:
        logger.info("Notification sent: %s - %s (%s)", title, message, event)