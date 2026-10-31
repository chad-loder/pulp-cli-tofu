import os
import typing as t

import pytest

pytest_plugins = "pytest_pulp_cli"


@pytest.fixture
def pulp_cli_vars(pulp_cli_vars: t.MutableMapping[str, str]) -> t.MutableMapping[str, str]:
    result: t.MutableMapping[str, str] = {}
    result.update(pulp_cli_vars)
    result["TOFU_REGISTRY_URL"] = os.environ.get(
        "TOFU_REGISTRY_URL", "https://registry.opentofu.org/"
    )
    return result
