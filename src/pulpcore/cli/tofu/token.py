import click
from pulp_cli.generic import (
    PulpCLIContext,
    create_command,
    destroy_command,
    href_option,
    list_command,
    pass_pulp_context,
    pulp_group,
    show_command,
)

from pulp_glue.common.context import DATETIME_FORMATS
from pulp_glue.common.i18n import get_translation
from pulp_glue.tofu.context import PulpTofuTokenContext

translation = get_translation(__package__)
_ = translation.gettext


@pulp_group()
@pass_pulp_context
@click.pass_context
def token(ctx: click.Context, pulp_ctx: PulpCLIContext, /) -> None:
    """Your registry tokens, for OpenTofu's TF_TOKEN_<host>."""
    ctx.obj = PulpTofuTokenContext(pulp_ctx)


create_options = [
    click.option("--name", required=True, help=_("A label for the token.")),
    click.option(
        "--namespace",
        "namespaces",
        multiple=True,
        required=True,
        help=_("href of a namespace the token covers; repeatable."),
    ),
    click.option(
        "--scope",
        type=click.Choice(["read", "update", "publish"]),
        default="read",
        help=_(
            "read reads; update also publishes new versions of existing providers and "
            "modules; publish also publishes new ones."
        ),
    ),
    click.option(
        "--expires-at",
        # pulp-glue validates date-time fields as datetime objects, not strings.
        type=click.DateTime(formats=[*DATETIME_FORMATS, "%Y-%m-%dT%H:%M:%S%z"]),
        help=_("Time the token stops working, e.g. 2027-01-01T00:00:00Z."),
    ),
]

token.add_command(list_command())
token.add_command(show_command(decorators=[href_option]))
token.add_command(create_command(decorators=create_options))
token.add_command(destroy_command(decorators=[href_option]))
