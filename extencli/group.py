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

    def __init__(self, *args: Any, depends_on: str|list[str], **kwargs: Any) -> None:
        """Construct the PluginAutoloaderGroup.

        Custom arguments include:
         - depends_on: the importable name(s) of the module that embarks the
           group configured as a PluginAutoloaderGroup. Can be either a single
           string (the module's name) or a list of strings (list of alternative
           module names, for cases encompassing dashes or underscores)
        """
        super().__init__(*args, **kwargs)
        dependencies = []
        if isinstance(depends_on, str):
            dependencies.append(depends_on)
        else:
            dependencies.extend(depends_on)
        self._dependency_names = dependencies
        self._extended: bool = False

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
            reqs = [d for dep in pkg_dist[pkg_name] for d in cls._requires(pkg_dist, dep)]
        return reqs

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
            # Find those that depend on any of the self._dependency_names directly
            if any(
                any(ref in spec for ref in self._dependency_names)
                for spec in self._requires(pkg_dist, pkg_name)
            ):
                # Import them. Should be sufficient to record sub-commands and groups,
                # as the click.Group should handle that.
                import_module(pkg_name)

        self._extended = True
