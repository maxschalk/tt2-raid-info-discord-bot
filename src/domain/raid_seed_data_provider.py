from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

# pylint: disable=import-error
from src.model.seed_type import SeedType


class RaidSeedDataProvider(ABC):

    @abstractmethod
    def list_seed_identifiers(self: RaidSeedDataProvider,
                              *,
                              seed_type: SeedType = SeedType.RAW) -> list[str]:
        pass

    @abstractmethod
    def save_seed(self: RaidSeedDataProvider, *, identifier: str,
                  data: list[Any]) -> bool:
        pass

    @abstractmethod
    def get_seed(
        self: RaidSeedDataProvider,
        *,
        identifier: str,
        seed_type: SeedType = SeedType.RAW,
    ) -> list[Any] | None:
        pass

    @abstractmethod
    def delete_seed(
        self: RaidSeedDataProvider,
        *,
        identifier: str,
    ) -> bool:
        pass
