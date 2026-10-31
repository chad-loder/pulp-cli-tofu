import click
from pulp_cli.generic import (
    content_filter_options,
    href_option,
    list_command,
    pulp_group,
    pulp_option,
    show_command,
    type_option,
)

from pulp_glue.common.i18n import get_translation
from pulp_glue.tofu.context import (
    PulpModuleVersionContext,
    PulpProviderPackageContext,
    PulpProviderVersionContext,
)

translation = get_translation(__package__)
_ = translation.gettext


@pulp_group()
@type_option(
    choices={
        "provider_version": PulpProviderVersionContext,
        "provider_package": PulpProviderPackageContext,
        "module_version": PulpModuleVersionContext,
    },
    default="provider_version",
)
def content() -> None:
    """Provider versions, provider packages and module versions Pulp holds."""


filter_options = [
    *content_filter_options,
    pulp_option("--hostname"),
    pulp_option("--namespace"),
    pulp_option("--version"),
    pulp_option(
        "--provider-type",
        allowed_with_contexts=(PulpProviderVersionContext, PulpProviderPackageContext),
    ),
    pulp_option("--name", "name", allowed_with_contexts=(PulpModuleVersionContext,)),
    pulp_option("--system", allowed_with_contexts=(PulpModuleVersionContext,)),
    click.option("--sha256"),
]

content.add_command(list_command(decorators=filter_options))
content.add_command(show_command(decorators=[href_option]))
