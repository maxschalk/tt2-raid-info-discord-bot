from typing import Any, Callable

import requests
from requests import Response
from src.domain.raid_seed_data_provider import RaidSeedDataProvider
from src.domain.seed_type import SeedType
from src.utils.get_env import get_env


class RaidSeedDataAPI(RaidSeedDataProvider):

    def __init__(self, *, base_url: str = None, auth_key: str = None) -> None:
        super().__init__()

        self.base_url = base_url or get_env(key="RAID_SEED_DATA_API_BASE_URL")

        self.auth_key = auth_key or get_env(
            key="RAID_SEED_DATA_API_AUTH_SECRET")

        self.request_headers = {
            "secret": auth_key,
            "Accept": "application/json"
        }

    def _make_api_request(self,
                          *,
                          method: Callable,
                          path: str,
                          data: Any | None = None,
                          headers: dict[str, str] | None = None) -> Response:

        headers = self.request_headers | (headers or {})

        response = method(url=f"{self.base_url}/{path}",
                          headers=headers,
                          data=data)

        response.raise_for_status()

        return response

    def list_seed_identifiers(self: RaidSeedDataProvider,
                              *,
                              seed_type: SeedType = SeedType.RAW) -> list[str]:

        response = self._make_api_request(
            method=requests.get,
            path=f"admin/all_seed_filenames/{seed_type.value}")

        return response.json()

    def save_seed(self: RaidSeedDataProvider, *, identifier: str,
                  data: str) -> None:

        self._make_api_request(method=requests.post,
                               path=f"admin/raw_seed_file/{identifier}",
                               data=data)

    def get_seed(
        self: RaidSeedDataProvider,
        *,
        identifier: str,
        seed_type: SeedType = SeedType.RAW,
    ) -> list[Any]:

        response = self._make_api_request(
            method=requests.get,
            path=f"admin/seed_file/{seed_type.value}/{identifier}")

        return response.json()

    def delete_seed(
        self: RaidSeedDataProvider,
        *,
        identifier: str,
    ) -> None:

        response = self._make_api_request(
            method=requests.delete, path=f"admin/raw_seed_file/{identifier}")

        data = response.json()

        if not data.get("deleted", False):
            raise ValueError(
                f"Seed {identifier} was not deleted: {data.get('detail', data)}"
            )
