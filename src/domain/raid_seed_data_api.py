from typing import Any, Callable, Union

import requests
from requests import Response
from src.domain.raid_seed_data_provider import RaidSeedDataProvider
from src.domain.seed_type import SeedType


class RaidSeedDataAPI(RaidSeedDataProvider):

    def __init__(self, *, base_url: str, auth_key: str) -> None:
        super().__init__()

        self.base_url = base_url

        self.auth_key = auth_key

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
            path=f"admin/seed_identifiers/{seed_type.value}")

        return response.json()

    def save_seed(self: RaidSeedDataProvider, *, identifier: str,
                  data: str) -> None:

        self._make_api_request(method=requests.post,
                               path=f"admin/save/{identifier}",
                               data=data)

    def get_seed(
        self: RaidSeedDataProvider,
        *,
        identifier: str,
        seed_type: SeedType = SeedType.RAW,
    ) -> list[Any]:

        response = self._make_api_request(
            method=requests.get,
            path=f"admin/seed/{seed_type.value}/{identifier}")

        return response.json()

    def delete_seed(
        self: RaidSeedDataProvider,
        *,
        identifier: str,
    ) -> None:

        self._make_api_request(method=requests.delete,
                               path=f"admin/delete/{identifier}")

    def delete_seeds_older_than(self: RaidSeedDataProvider,
                                *,
                                days: Union[int, None] = None) -> None:

        query = "" if days is None else f"days={days}"

        self._make_api_request(method=requests.delete,
                               path=f"admin/delete_old?{query}")
