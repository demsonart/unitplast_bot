import logging
import os
from enum import Enum
from typing import List, Dict, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification event types"""

    NEW_ORDER = ("🟢", "Новый заказ")
    PRICE_REQUEST = ("🟡", "Запрос цены")
    EMAIL = ("🔵", "Email")
    DOCUMENTS = ("🟣", "Документы")
    SYSTEM_ERROR = ("🔴", "Ошибка системы")
    PRODUCTION = ("⚫", "Производство")


class NotificationTarget:
    """Notification group configuration"""

    def __init__(
        self,
        name: str,
        group_id: Optional[int],
        notification_types: List[str],
        is_active: bool = True,
    ):
        self.name = name  # SALES, PRODUCTION, MANAGEMENT, TEST
        self.group_id = group_id  # Telegram group ID
        self.notification_types = notification_types
        self.is_active = is_active

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "group_id": self.group_id,
            "notification_types": self.notification_types,
            "is_active": self.is_active,
        }

    @staticmethod
    def from_dict(data: dict) -> "NotificationTarget":
        return NotificationTarget(
            name=data["name"],
            group_id=data.get("group_id"),
            notification_types=data.get("notification_types", []),
            is_active=data.get("is_active", True),
        )


class NotificationRouter:
    """Route notifications to appropriate targets"""

    CONFIG_PATH = Path("./config/notification_targets.json")

    def __init__(self):
        self.targets: Dict[str, NotificationTarget] = {}
        self._load_or_create_defaults()

    def _load_or_create_defaults(self):
        """Load existing config or create defaults"""
        if self.CONFIG_PATH.exists():
            try:
                with open(self.CONFIG_PATH) as f:
                    data = json.load(f)
                    for name, target_data in data.items():
                        self.targets[name] = NotificationTarget.from_dict(target_data)
                logger.info(f"Loaded {len(self.targets)} notification targets")
            except Exception as e:
                logger.error(f"Error loading config: {e}, creating defaults")
                self._create_defaults()
        else:
            self._create_defaults()

    def _create_defaults(self):
        """Create default notification groups"""
        defaults = {
            "TEST": NotificationTarget(
                name="TEST",
                group_id=None,  # Will be set via UI
                notification_types=["NEW_ORDER", "PRICE_REQUEST", "SYSTEM_ERROR"],
                is_active=True,
            ),
            "SALES": NotificationTarget(
                name="SALES",
                group_id=None,
                notification_types=["NEW_ORDER", "PRICE_REQUEST"],
                is_active=True,
            ),
            "PRODUCTION": NotificationTarget(
                name="PRODUCTION",
                group_id=None,
                notification_types=["PRODUCTION", "DOCUMENTS"],
                is_active=True,
            ),
            "MANAGEMENT": NotificationTarget(
                name="MANAGEMENT",
                group_id=None,
                notification_types=[
                    "NEW_ORDER",
                    "SYSTEM_ERROR",
                    "PRICE_REQUEST",
                ],
                is_active=True,
            ),
        }

        self.targets = defaults
        self._save_config()
        logger.info("Created default notification targets")

    def _save_config(self):
        """Save configuration to file"""
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_PATH, "w") as f:
            data = {name: target.to_dict() for name, target in self.targets.items()}
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Saved notification configuration")

    def add_target(
        self,
        name: str,
        group_id: int,
        notification_types: List[str],
    ) -> bool:
        """Add or update notification target"""
        if name in self.targets and self.targets[name].group_id is not None:
            logger.warning(f"Target {name} already exists, updating...")

        self.targets[name] = NotificationTarget(
            name=name,
            group_id=group_id,
            notification_types=notification_types,
            is_active=True,
        )
        self._save_config()
        logger.info(f"Added/updated target: {name} (group_id: {group_id})")
        return True

    def remove_target(self, name: str) -> bool:
        """Remove notification target"""
        if name in self.targets:
            del self.targets[name]
            self._save_config()
            logger.info(f"Removed target: {name}")
            return True
        return False

    def get_targets_for_event(
        self, event_type: str, priority: Optional[str] = None
    ) -> List[NotificationTarget]:
        """Get all active targets for an event type"""
        targets = []

        for target in self.targets.values():
            if not target.is_active:
                continue

            # Check if target handles this event type
            if event_type in target.notification_types:
                # For high-priority orders, notify management
                if priority == "CRITICAL" and target.name == "MANAGEMENT":
                    targets.append(target)
                elif priority != "CRITICAL":
                    targets.append(target)

        return targets

    def route_order(self, lead_data: dict) -> List[Dict]:
        """Route order to appropriate targets based on score and type"""
        routes = []

        order_type = lead_data.get("order_type", "🟢 ORDER")
        priority = lead_data.get("priority", {}).get("level", "LOW")
        score = lead_data.get("score", 0)

        # Convert order type to notification type
        if "PRODUCTION" in order_type:
            event_type = "PRODUCTION"
        elif "PRICE" in order_type:
            event_type = "PRICE_REQUEST"
        else:
            event_type = "NEW_ORDER"

        # Get targets
        targets = self.get_targets_for_event(event_type, priority)

        for target in targets:
            if target.group_id:
                routes.append(
                    {
                        "target": target.name,
                        "group_id": target.group_id,
                        "event_type": event_type,
                        "priority": priority,
                    }
                )

        logger.info(
            f"Routed order (score:{score}) to {len(routes)} targets: {[r['target'] for r in routes]}"
        )
        return routes

    def get_all_targets(self) -> List[Dict]:
        """Get all configured targets"""
        return [target.to_dict() for target in self.targets.values()]

    def test_connection(self, target_name: str) -> bool:
        """Test if target is reachable (stub for future implementation)"""
        target = self.targets.get(target_name)
        if not target or not target.group_id:
            return False
        # Actual connection test would go here
        return True
