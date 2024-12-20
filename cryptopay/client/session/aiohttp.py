import ssl
from typing import TYPE_CHECKING, cast

import certifi
from aiohttp import ClientSession, TCPConnector
from aiohttp.http import SERVER_SOFTWARE

from cryptopay.__meta__ import __version__

from .base import BaseSession

if TYPE_CHECKING:
    import cryptopay
    from cryptopay.client import APIServer
    from cryptopay.methods import CryptoPayMethod
    from cryptopay.types import _CryptoPayType


class AiohttpSession(BaseSession):
    """
    Http session based on aiohttp.

    This class is a wrapper of `aiohttp.ClientSession`.
    """

    def __init__(self, api_server: "APIServer") -> None:
        super().__init__(api_server)
        self._session: ClientSession | None = None

    async def request(
        self,
        token: str,
        client: "cryptopay.CryptoPay",
        method: "CryptoPayMethod[_CryptoPayType]",
    ) -> "_CryptoPayType":
        """Make http request."""
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._session = ClientSession(
            connector=TCPConnector(
                ssl_context=ssl_context,
            ),
        )
        async with self._session as session:
            resp = await session.post(
                url=self.api_server.url(method),
                data=method.model_dump_json(exclude_none=True),
                headers={
                    "Crypto-Pay-API-Token": token,
                    "Content-Type": "application/json",
                    "User-Agent": f"{SERVER_SOFTWARE} aiocpa/{__version__}",
                },
            )
            response = self._check_response(client, method, await resp.text())
        return cast("_CryptoPayType", response.result)

    async def close(self) -> None:
        """Close http session."""
        if self._session is not None and not self._session.closed:
            await self._session.close()

    def __del__(self) -> None:
        """Close session connector."""
        if (
            self._session is not None
            and not self._session.closed
            and self._session.connector is not None
            and self._session.connector_owner
        ):
            self._session.connector.close()
