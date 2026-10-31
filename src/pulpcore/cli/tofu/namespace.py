from pathlib import Path

import click
from pulp_cli.generic import (
    PulpCLIContext,
    chunk_size_option,
    create_command,
    destroy_command,
    href_option,
    list_command,
    name_option,
    pass_entity_context,
    pass_pulp_context,
    pulp_group,
    resource_lookup_option,
    resource_option,
    role_command,
    show_command,
    update_command,
)

from pulp_glue.common.context import PulpEntityContext
from pulp_glue.common.i18n import get_translation
from pulp_glue.tofu.context import PulpTofuDistributionContext, PulpTofuNamespaceContext

translation = get_translation(__package__)
_ = translation.gettext

namespace_lookup_option = resource_lookup_option(
    "--namespace", context_class=PulpTofuNamespaceContext
)


@pulp_group()
@pass_pulp_context
@click.pass_context
def namespace(ctx: click.Context, pulp_ctx: PulpCLIContext, /) -> None:
    """Registry namespaces: who reads and publishes each one, and what serves it."""
    ctx.obj = PulpTofuNamespaceContext(pulp_ctx)


lookup_options = [href_option, name_option, namespace_lookup_option]
namespace_options = [
    resource_option(
        "--distribution",
        default_plugin="tofu",
        default_type="tofu",
        context_table={"tofu:tofu": PulpTofuDistributionContext},
        href_pattern=PulpTofuDistributionContext.HREF_PATTERN,
        help=_("The distribution whose repository the registry serves for this namespace."),
    ),
    click.option(
        "--content-hostname",
        help=_("Origin hostname of the content served, e.g. registry.opentofu.org."),
    ),
    click.option("--private/--public", default=None),
    click.option("--keyring", help=_("href of the OpenPGP keyring that signs releases.")),
    click.option(
        "--signing-service",
        help=_("href of a tofu signing service that signs unsigned releases."),
    ),
]

namespace.add_command(list_command(decorators=[name_option]))
namespace.add_command(show_command(decorators=lookup_options))
namespace.add_command(
    create_command(decorators=[click.option("--name", required=True), *namespace_options])
)
namespace.add_command(update_command(decorators=lookup_options + namespace_options))
namespace.add_command(destroy_command(decorators=lookup_options))
namespace.add_command(role_command(decorators=lookup_options))


@namespace.command()
@href_option
@name_option
@namespace_lookup_option
@chunk_size_option
@click.argument(
    "files", nargs=-1, required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@pass_entity_context
@pass_pulp_context
def publish(
    pulp_ctx: PulpCLIContext,
    namespace_ctx: PulpEntityContext,
    /,
    files: tuple[Path, ...],
    chunk_size: int | None,
) -> None:
    """Publish a provider release from GoReleaser's files, e.g. dist/terraform-provider-*."""
    assert isinstance(namespace_ctx, PulpTofuNamespaceContext)
    result = namespace_ctx.publish(list(files), chunk_size=chunk_size)
    pulp_ctx.output_result(result)


@namespace.command("publish-module")
@href_option
@name_option
@namespace_lookup_option
@chunk_size_option
@click.option("--module", "module_name", required=True, help=_("Module name, e.g. vpc."))
@click.option("--system", required=True, help=_("Target system, e.g. aws."))
@click.option("--version", required=True, help=_("SemVer 2.0 version."))
@click.argument("package", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@pass_entity_context
@pass_pulp_context
def publish_module(
    pulp_ctx: PulpCLIContext,
    namespace_ctx: PulpEntityContext,
    /,
    module_name: str,
    system: str,
    version: str,
    package: Path,
    chunk_size: int | None,
) -> None:
    """Publish a module version from a .tar.gz of its directory."""
    assert isinstance(namespace_ctx, PulpTofuNamespaceContext)
    result = namespace_ctx.publish_module(
        module_name, system, version, package, chunk_size=chunk_size
    )
    pulp_ctx.output_result(result)
