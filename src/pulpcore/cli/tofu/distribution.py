import click
from pulp_cli.generic import (
    content_guard_option,
    create_command,
    destroy_command,
    distribution_filter_options,
    distribution_lookup_option,
    href_option,
    label_command,
    list_command,
    name_option,
    pulp_group,
    pulp_labels_option,
    resource_option,
    role_command,
    show_command,
    type_option,
    update_command,
)

from pulp_glue.common.i18n import get_translation
from pulp_glue.tofu.context import (
    PulpTofuDistributionContext,
    PulpTofuRemoteContext,
    PulpTofuRepositoryContext,
)

translation = get_translation(__package__)
_ = translation.gettext


@pulp_group()
@type_option(choices={"tofu": PulpTofuDistributionContext})
def distribution() -> None:
    """Network mirrors, and the repositories registry namespaces serve."""


lookup_options = [href_option, name_option, distribution_lookup_option]
distribution_options = [
    click.option("--base-path"),
    resource_option(
        "--repository",
        default_plugin="tofu",
        default_type="tofu",
        context_table={"tofu:tofu": PulpTofuRepositoryContext},
        href_pattern=PulpTofuRepositoryContext.HREF_PATTERN,
    ),
    resource_option(
        "--remote",
        default_plugin="tofu",
        default_type="tofu",
        context_table={"tofu:tofu": PulpTofuRemoteContext},
        href_pattern=PulpTofuRemoteContext.HREF_PATTERN,
        help=_("Remote that fetches providers not yet in Pulp."),
    ),
    content_guard_option,
    click.option(
        "--allow-uploads/--no-allow-uploads",
        default=None,
        help=_("Accept releases published to the namespaces this distribution serves."),
    ),
    pulp_labels_option,
]

distribution.add_command(list_command(decorators=distribution_filter_options))
distribution.add_command(show_command(decorators=lookup_options))
distribution.add_command(
    create_command(decorators=[click.option("--name", required=True), *distribution_options])
)
distribution.add_command(update_command(decorators=lookup_options + distribution_options))
distribution.add_command(destroy_command(decorators=lookup_options))
distribution.add_command(label_command(decorators=[distribution_lookup_option]))
distribution.add_command(role_command(decorators=lookup_options))
