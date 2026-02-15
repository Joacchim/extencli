# extencli

A set of utilities around click, which offers extensible CLI mechanism, with little effort

## Features

### Easy third-party extensible click.group

This package offers a specialized
[click.group](https://click.palletsprojects.com/en/stable/api/#click.Group)
implementation. Using it, you can create a CLI that will be extended by
simply installing additional modules.

As an example, here is how one would define an extensible `click.group` in
their python package `core_module`:

```python
import click

from extencli import PluginAutoloaderGroup

@click.group('core', cls=PluginAutoloaderGroup, depends_on='core_module')
def core_group():
    ...
```

The `depends_on` parameter is required:
 - `depends_on` specifies the name of the package that CLI
   extensions should depend on

Now, the CLI extension package should import the `core_group` from the
`core_module` like so:

```python
from core_module.cli import core_group

@core_group.command('myext')
def cli_extension():
    ...
```

Now, by simply installing both the `core_module` and the `extension`
third-party, the `core_module` will be extended with the `myext` command:

```shell
$> core --help
Usage: core [OPTIONS] COMMAND [ARGS]...

Options:
  --help                          Show this message and exit.

Commands:
  myext
```

### Caveats

#### Silent "failure" to load extensions

If the base CLI has its extensible group declared in the `__init__.py` file,
the internal `click` initialization mechanism might use different instances of
the group when loaded by extensions, and when invoked through the CLI.

To avoid this, please refer to the tests's `tests/python_packages/test_core`
python module, which is built in a way that avoid this caveat:
 - extensible group should not be in the `__init__.py` file
 - `pyproject.toml` may refer directly to it for script entrypoints
