import typing as t
from pathlib import Path

from pulp_glue.common.context import (
    EntityDefinition,
    PluginRequirement,
    PulpContentContext,
    PulpDistributionContext,
    PulpEntityContext,
    PulpRemoteContext,
    PulpRepositoryContext,
    PulpRepositoryVersionContext,
)
from pulp_glue.common.i18n import get_translation
from pulp_glue.core.context import PulpArtifactContext

translation = get_translation(__package__)
_ = translation.gettext

PLUGIN = "tofu"


class PulpProviderVersionContext(PulpContentContext):
    ENTITY = _("provider version")
    ENTITIES = _("provider versions")
    HREF = "tofu_provider_version_href"
    ID_PREFIX = "content_tofu_provider_versions"
    NEEDS_PLUGINS = [PluginRequirement(PLUGIN)]
    PLUGIN = PLUGIN
    RESOURCE_TYPE = "provider_version"


class PulpProviderPackageContext(PulpContentContext):
    ENTITY = _("provider package")
    ENTITIES = _("provider packages")
    HREF = "tofu_provider_package_href"
    ID_PREFIX = "content_tofu_provider_packages"
    NEEDS_PLUGINS = [PluginRequirement(PLUGIN)]
    PLUGIN = PLUGIN
    RESOURCE_TYPE = "provider_package"


class PulpModuleVersionContext(PulpContentContext):
    ENTITY = _("module version")
    ENTITIES = _("module versions")
    HREF = "tofu_module_version_href"
    ID_PREFIX = "content_tofu_module_versions"
    NEEDS_PLUGINS = [PluginRequirement(PLUGIN)]
    PLUGIN = PLUGIN
    RESOURCE_TYPE = "module_version"


class PulpTofuRemoteContext(PulpRemoteContext):
    ENTITY = _("tofu remote")
    ENTITIES = _("tofu remotes")
    HREF = "tofu_tofu_remote_href"
    ID_PREFIX = "remotes_tofu_tofu"
    NEEDS_PLUGINS = [PluginRequirement(PLUGIN)]
    PLUGIN = PLUGIN
    RESOURCE_TYPE = "tofu"


class PulpTofuRepositoryVersionContext(PulpRepositoryVersionContext):
    HREF = "tofu_tofu_repository_version_href"
    REPOSITORY_HREF = "tofu_tofu_repository_href"
    ID_PREFIX = "repositories_tofu_tofu_versions"
    NEEDS_PLUGINS = [PluginRequirement(PLUGIN)]


class PulpTofuRepositoryContext(PulpRepositoryContext):
    ENTITY = _("tofu repository")
    ENTITIES = _("tofu repositories")
    HREF = "tofu_tofu_repository_href"
    ID_PREFIX = "repositories_tofu_tofu"
    NEEDS_PLUGINS = [PluginRequirement(PLUGIN)]
    PLUGIN = PLUGIN
    RESOURCE_TYPE = "tofu"
    VERSION_CONTEXT = PulpTofuRepositoryVersionContext


class PulpTofuDistributionContext(PulpDistributionContext):
    ENTITY = _("tofu distribution")
    ENTITIES = _("tofu distributions")
    HREF = "tofu_tofu_distribution_href"
    ID_PREFIX = "distributions_tofu_tofu"
    NEEDS_PLUGINS = [PluginRequirement(PLUGIN)]
    NULLABLES = {"remote", "repository", "content_guard"}
    PLUGIN = PLUGIN
    RESOURCE_TYPE = "tofu"


class PulpTofuNamespaceContext(PulpEntityContext):
    ENTITY = _("tofu namespace")
    ENTITIES = _("tofu namespaces")
    HREF = "tofu_tofu_namespace_href"
    ID_PREFIX = "pulp_tofu_namespaces"
    NEEDS_PLUGINS = [PluginRequirement(PLUGIN)]
    NULLABLES = {"distribution", "keyring", "signing_service"}

    def publish(self, files: t.Sequence[Path], chunk_size: int | None = None) -> t.Any:
        """Publish one provider release from its files, named as GoReleaser names them.

        Each file is uploaded as an artifact first, in chunks of ``chunk_size`` bytes,
        or reused when Pulp already holds it. The release then names the artifacts in
        one ``artifacts`` object of filename to artifact href.
        """
        body: EntityDefinition = {
            "artifacts": {path.name: self._artifact(path, chunk_size) for path in files}
        }
        return self.call("publish", parameters={self.HREF: self.pulp_href}, body=body)

    def publish_module(
        self,
        name: str,
        system: str,
        version: str,
        package: Path,
        chunk_size: int | None = None,
    ) -> t.Any:
        """Publish one module version from its ``.tar.gz``."""
        body: EntityDefinition = {
            "name": name,
            "system": system,
            "version": version,
            "artifact": self._artifact(package, chunk_size),
        }
        return self.call("publish_module", parameters={self.HREF: self.pulp_href}, body=body)

    def _artifact(self, path: Path, chunk_size: int | None) -> str:
        with path.open("rb") as upload:
            return str(PulpArtifactContext(self.pulp_ctx).upload(upload, chunk_size))


class PulpTofuTokenContext(PulpEntityContext):
    ENTITY = _("tofu token")
    ENTITIES = _("tofu tokens")
    HREF = "tofu_tofu_token_href"
    ID_PREFIX = "pulp_tofu_tokens"
    NEEDS_PLUGINS = [PluginRequirement(PLUGIN)]
