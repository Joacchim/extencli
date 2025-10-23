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

    Loads all modules depending on the specified `depends_on` package name, and
    records the attribute matching the provided `load_attr` as a command part
    of the extensible click.Group.
    """

    def __init__(self, *args: Any, depends_on: str|list[str], load_attr: str, **kwargs: Any) -> None:
        """Construct the PluginAutoloaderGroup.

        Custom arguments include:
         - depends_on: the importable name(s) of the module that embarks the
           group configured as a PluginAutoloaderGroup. Can be either a single
           string (the module's name) or a list of strings (list of alternative
           module names, for cases encompassing dashes or underscores)
         - load_attr: the fixed name of the attribute to be looked-up in
           each of the extending modules, that depend on the extensible
           package. Used to keep track of subcommands for help-text generation
           and subcommand execution.
        """
        super().__init__(*args, **kwargs)
        dependencies = []
        if isinstance(depends_on, str):
            dependencies.append(depends_on)
        else:
            dependencies.extend(depends_on)
        self._dependency_names = dependencies
        self._attrname = load_attr
        self._extensions: dict[str, click.Command] = {}

    def list_commands(self, ctx: click.Context) -> list[str]:
        """List commands including autoloaded extensions."""
        self._extend()
        base = super().list_commands(ctx)
        extended = sorted(self._extensions.keys())
        return base + extended

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command|None:
        """Retrieve subcommand including autoloaded extensions."""
        self._extend()
        if cmd_name in self._extensions:
            return self._extensions[cmd_name]
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
        if self._extensions:
            return

        # Iterate all installed packages
        pkg_dist = packages_distributions()
        for pkg_name in pkg_dist:
            # Find those that depend on any of the self._dependency_names directly
            if any(
                any(ref in spec for ref in self._dependency_names)
                for spec in self._requires(pkg_dist, pkg_name)
            ):
                # Import them, and record their `.{self._attrname}` attribute as the subcommand_object
                module = import_module(pkg_name)
                cmd_object = getattr(module, self._attrname)
                self._extensions[cmd_object.name] = cmd_object
