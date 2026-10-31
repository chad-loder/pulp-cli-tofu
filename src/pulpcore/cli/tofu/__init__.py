import typing as t

import click
from pulp_cli.generic import pulp_group

from pulp_glue.common.i18n import get_translation

from pulpcore.cli.tofu.content import content
from pulpcore.cli.tofu.distribution import distribution
from pulpcore.cli.tofu.namespace import namespace
from pulpcore.cli.tofu.remote import remote
from pulpcore.cli.tofu.repository import repository
from pulpcore.cli.tofu.token import token

translation = get_translation(__package__)
_ = translation.gettext

__version__ = "0.0.1.dev0"


@pulp_group(name="tofu")
def tofu_group() -> None:
    """OpenTofu providers and modules: mirrors, registry namespaces and tokens."""


def mount(main: click.Group, **kwargs: t.Any) -> None:
    for command in (content, distribution, namespace, remote, repository, token):
        tofu_group.add_command(command)
    main.add_command(tofu_group)
