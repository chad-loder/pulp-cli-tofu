import click
from pulp_cli.generic import (
    common_remote_create_options,
    common_remote_update_options,
    create_command,
    destroy_command,
    href_option,
    label_command,
    label_select_option,
    list_command,
    name_option,
    pulp_group,
    role_command,
    show_command,
    type_option,
    update_command,
)

from pulp_glue.common.i18n import get_translation
from pulp_glue.tofu.context import PulpTofuRemoteContext

translation = get_translation(__package__)
_ = translation.gettext


@pulp_group()
@type_option(choices={"tofu": PulpTofuRemoteContext})
def remote() -> None:
    """An upstream OpenTofu registry."""


lookup_options = [href_option, name_option]
tofu_remote_options = [
    click.option(
        "--policy", type=click.Choice(["immediate", "on_demand", "streamed"], case_sensitive=False)
    ),
    click.option(
        "--include",
        "includes",
        multiple=True,
        help=_("hostname/namespace/type glob a provider must match; repeatable."),
    ),
    click.option(
        "--exclude",
        "excludes",
        multiple=True,
        help=_("hostname/namespace/type glob a provider must not match; repeatable."),
    ),
    click.option(
        "--metadata-ttl",
        type=int,
        help=_("Seconds an upstream version list is reused before refreshing."),
    ),
    click.option(
        "--require-signatures/--no-require-signatures",
        default=None,
        help=_("Refuse unsigned providers, even from registry.opentofu.org."),
    ),
    click.option(
        "--signing-key",
        "signing_keys",
        multiple=True,
        help=_("Fingerprint of a key trusted to sign providers; repeatable."),
    ),
]

remote.add_command(list_command(decorators=[label_select_option]))
remote.add_command(show_command(decorators=lookup_options))
remote.add_command(create_command(decorators=common_remote_create_options + tofu_remote_options))
remote.add_command(
    update_command(decorators=lookup_options + common_remote_update_options + tofu_remote_options)
)
remote.add_command(destroy_command(decorators=lookup_options))
remote.add_command(label_command(decorators=lookup_options))
remote.add_command(role_command(decorators=lookup_options))
