import typing as t

import click
from pulp_cli.generic import (
    create_command,
    destroy_command,
    href_option,
    label_command,
    label_select_option,
    list_command,
    name_option,
    pass_repository_context,
    pulp_group,
    repository_href_option,
    repository_lookup_option,
    resource_option,
    retained_versions_option,
    role_command,
    show_command,
    type_option,
    update_command,
    version_command,
)
from pulpcore.cli.core.generic import task_command

from pulp_glue.common.context import (
    EntityFieldDefinition,
    PulpEntityContext,
    PulpRepositoryContext,
)
from pulp_glue.common.i18n import get_translation
from pulp_glue.tofu.context import PulpTofuRemoteContext, PulpTofuRepositoryContext

translation = get_translation(__package__)
_ = translation.gettext

remote_option = resource_option(
    "--remote",
    default_plugin="tofu",
    default_type="tofu",
    context_table={"tofu:tofu": PulpTofuRemoteContext},
    href_pattern=PulpTofuRemoteContext.HREF_PATTERN,
)


@pulp_group()
@type_option(choices={"tofu": PulpTofuRepositoryContext})
def repository() -> None:
    """Repositories of providers and modules."""


lookup_options = [href_option, name_option]
nested_lookup_options = [repository_href_option, repository_lookup_option]
update_options = [click.option("--description"), remote_option, retained_versions_option]
create_options = [*update_options, click.option("--name", required=True)]

repository.add_command(list_command(decorators=[label_select_option]))
repository.add_command(show_command(decorators=lookup_options))
repository.add_command(create_command(decorators=create_options))
repository.add_command(update_command(decorators=lookup_options + update_options))
repository.add_command(destroy_command(decorators=lookup_options))
repository.add_command(task_command(decorators=nested_lookup_options))
repository.add_command(version_command(decorators=nested_lookup_options))
repository.add_command(label_command(decorators=nested_lookup_options))
repository.add_command(role_command(decorators=lookup_options))


def _selection(text: str) -> dict[str, t.Any]:
    """``namespace/type[@version,...]`` or ``namespace/name/system[@version,...]``."""
    address, _sep, versions = text.partition("@")
    parts = address.split("/")
    selection: dict[str, t.Any] = {"namespace": parts[0]}
    if len(parts) == 2:
        selection["type"] = parts[1]
    elif len(parts) == 3:
        selection.update(name=parts[1], system=parts[2])
    else:
        raise click.BadParameter(_("expected namespace/type or namespace/name/system"))
    if versions:
        selection["versions"] = versions.split(",")
    return selection


@repository.command()
@name_option
@href_option
@remote_option
@click.option(
    "--provider",
    "providers",
    multiple=True,
    help=_("namespace/type[@version,...] to fetch; repeatable, e.g. hashicorp/aws@5.80.0."),
)
@click.option(
    "--module",
    "modules",
    multiple=True,
    help=_("namespace/name/system[@version,...] to fetch; repeatable."),
)
@click.option("--latest", type=int, help=_("Newest releases to fetch when no version is given."))
@click.option(
    "--platform",
    "platforms",
    multiple=True,
    help=_("os_arch provider platform to fetch, e.g. linux_amd64; repeatable."),
)
@click.option(
    "--mirror/--no-mirror",
    default=None,
    help=_("Remove from the repository what this sync does not select."),
)
@pass_repository_context
def sync(
    repository_ctx: PulpRepositoryContext,
    /,
    remote: EntityFieldDefinition,
    providers: tuple[str, ...],
    modules: tuple[str, ...],
    latest: int | None,
    platforms: tuple[str, ...],
    mirror: bool | None,
) -> None:
    """Fetch the selected providers and modules from the remote."""
    if not providers and not modules:
        raise click.UsageError(_("Select at least one --provider or --module."))
    body: dict[str, t.Any] = {}
    for key, values in (("providers", providers), ("modules", modules)):
        if values:
            selections = [_selection(value) for value in values]
            if latest is not None:
                for selection in selections:
                    selection.setdefault("latest", latest)
            body[key] = selections
    if platforms:
        body["platforms"] = list(platforms)
    if mirror is not None:
        body["mirror"] = mirror
    if isinstance(remote, PulpEntityContext):
        body["remote"] = remote
    elif repository_ctx.entity["remote"] is None:
        raise click.ClickException(
            _("Repository '{name}' has no default remote; pass --remote.").format(
                name=repository_ctx.entity["name"]
            )
        )
    repository_ctx.sync(body=body)
