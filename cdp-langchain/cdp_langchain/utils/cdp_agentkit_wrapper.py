"""Util that calls CDP."""

import inspect
import json
from collections.abc import Callable
from typing import Any

from langchain_core.utils import get_from_dict_or_env
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, model_validator

from cdp import Wallet
from cdp_langchain import __version__
from cdp_langchain.constants import CDP_LANGCHAIN_DEFAULT_SOURCE


class CdpAgentkitWrapper(BaseModel):
    """Wrapper for CDP Agentkit Core."""

    wallet: Any = None  #: :meta private:
    cdp_api_key_name: str | None = None
    cdp_api_key_private_key: str | None = None
    network_id: str | None = None
    openrouter_api_key: str | None = None
    openrouter_base_url: str | None = None
    model_name: str = "gpt-4"

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: dict) -> Any:
        """Validate that CDP API Key and python package exists in the environment and configure the CDP SDK."""
        cdp_api_key_name = get_from_dict_or_env(values, "cdp_api_key_name", "CDP_API_KEY_NAME")
        cdp_api_key_private_key = get_from_dict_or_env(
            values, "cdp_api_key_private_key", "CDP_API_KEY_PRIVATE_KEY"
        )
        network_id = get_from_dict_or_env(values, "network_id", "NETWORK_ID", "base-sepolia")
        wallet_data_json = values.get("cdp_wallet_data")

        # Add OpenRouter configuration
        openrouter_api_key = get_from_dict_or_env(
            values, "openrouter_api_key", "OPENROUTER_API_KEY", None
        )
        openrouter_base_url = get_from_dict_or_env(
            values,
            "openrouter_base_url",
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        )
        model_name = get_from_dict_or_env(values, "model_name", "MODEL_NAME", "gpt-4")

        try:
            from cdp import Cdp, Wallet, WalletData
        except Exception:
            raise ImportError(
                "CDP SDK is not installed. " "Please install it with `pip install cdp-sdk`"
            ) from None

        Cdp.configure(
            api_key_name=cdp_api_key_name,
            private_key=cdp_api_key_private_key,
            source=CDP_LANGCHAIN_DEFAULT_SOURCE,
            source_version=__version__,
        )

        if wallet_data_json:
            wallet_data = WalletData.from_dict(json.loads(wallet_data_json))
            wallet = Wallet.import_data(wallet_data)
        else:
            wallet = Wallet.create(network_id=network_id)

        values["wallet"] = wallet
        values["cdp_api_key_name"] = cdp_api_key_name
        values["cdp_api_key_private_key"] = cdp_api_key_private_key
        values["network_id"] = network_id
        values["openrouter_api_key"] = openrouter_api_key
        values["openrouter_base_url"] = openrouter_base_url
        values["model_name"] = model_name

        return values

    def export_wallet(self) -> dict[str, str]:
        """Export wallet data required to re-instantiate the wallet.

        Returns:
            str: The json string of wallet data including the wallet_id and seed.

        """
        wallet_data_dict = self.wallet.export_data().to_dict()

        wallet_data_dict["default_address_id"] = self.wallet.default_address.address_id

        return json.dumps(wallet_data_dict)

    def get_llm(self) -> ChatOpenAI:
        """Get a configured LLM instance.

        Returns:
            ChatOpenAI: The configured LLM instance, using OpenRouter if configured,
                       otherwise using default OpenAI configuration.
        """
        if self.openrouter_api_key:
            return ChatOpenAI(
                model=self.model_name,
                openai_api_key=self.openrouter_api_key,
                base_url=self.openrouter_base_url,
                headers={
                    "HTTP-Referer": "https://github.com/OpenRouterTeam/cdp-agentkit",
                    "X-Title": "CDP AgentKit",
                },
            )
        return ChatOpenAI(model=self.model_name)

    def run_action(self, func: Callable[..., str], **kwargs) -> str:
        """Run a CDP Action."""
        func_signature = inspect.signature(func)

        first_kwarg = next(iter(func_signature.parameters.values()), None)

        if first_kwarg and first_kwarg.annotation is Wallet:
            return func(self.wallet, **kwargs)
        else:
            return func(**kwargs)
