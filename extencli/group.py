"""Click Group extensions for auto-extension CLI mechanisms."""

from collections.abc import Mapping
from importlib.metadata import (  # type: ignore
    PackageNotFoundError,
    import_module,
    packages_distributions,
    requires,
)
from typing import Any

import click


class PluginAutoloaderGroup(click.Group):
    """Defines an auto-extensible click.Group.

    Loads all modules depending on the specified `depends_on` package name
    automatically, ensuring their additional groups and commands will be
    recorded into the click.Group through the usual mechanism.
    """

    def __init__(self, *args: Any, depends_on: str, **kwargs: Any) -> None:
        """Construct the PluginAutoloaderGroup.

        Custom arguments include:
         - depends_on: the importable name of the module that embarks the
           group configured as a PluginAutoloaderGroup.

        The PluginAutoloaderGroup considers package name after normalizing
        them, by replacing any underscore (`_`) by a dash, as the old
        PEP8/PEP625 confusion leads the distribution environment to have a mix
        of both characters, considered as interchangeable. Thus, however the
        input `depends_on` is formatted does not matter, as all extensions
        depending on any form of the provided name should be properly
        identified after normalization.
        """
        super().__init__(*args, **kwargs)
        self._dependency_name = self._normalize(depends_on)
        self._extended: bool = False

    @classmethod
    def _normalize(self, pkg_name: str) -> str:
        return pkg_name.replace('_', '-')

    def list_commands(self, ctx: click.Context) -> list[str]:
        """List commands including autoloaded extensions.

        Necessary to load the extensions only when the base CLI was fully
        loaded, reducing risk of dependency loops.
        """
        self._extend()
        return super().list_commands(ctx)

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command|None:
        """Retrieve subcommand including autoloaded extensions.

        Necessary to load the extensions only when the base CLI was fully
        loaded, reducing risk of dependency loops.
        """
        self._extend()
        return super().get_command(ctx, cmd_name)

    @classmethod
    def _requires(cls, pkg_dist: Mapping[str, list[str]], pkg_name: str) -> list[str]:
        """Resolve the dependencies of a package recursively."""
        reqs = []
        try:
            reqs = requires(pkg_name) or []
        except PackageNotFoundError:
            reqs = [
                d
                for dep in pkg_dist[pkg_name]
                for d in cls._requires(pkg_dist, dep)
            ]
        # Ensure we use only underscore base python package name, to
        # facilitate matching with the requested dependency.
        return [cls._normalize(req) for req in reqs]

    def _extend(self) -> None:
        """Import packages depending on the configured dependencies to extend the base CLI.

        This method also records the loaded extension to facilitate subcommand
        resolution from the loaded plugins.
        """
        # Only extend once
        if self._extended:
            return

        # Iterate all installed packages
        pkg_dist = packages_distributions()
        for pkg_name in pkg_dist:
            # Find those that depend on the self._dependency_name directly
            if any(
                self._dependency_name in spec
                for spec in self._requires(pkg_dist, pkg_name)
            ):
                # Import them. Should be sufficient to record sub-commands and groups,
                # as the click.Group should handle that.
                import_module(pkg_name)

        self._extended = True
