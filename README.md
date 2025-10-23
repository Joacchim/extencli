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

@click.group('core', cls=PluginAutoloaderGroup, depends_on='core_module', load_attr='cli_extension')
def core_group():
    ...
```

The `depends_on` and `load_attr` parameters are required:
 - `depends_on` specifies the name of the package that CLI
   extensions should depend on
 - `load_attr` states the symbol that CLI extensions must provide as
   subcommands of the `core_group`

Please note that the `load_attr` attribute defines that the `cli_extension`
symbol must be exposed as a top level attribute of any `core_module` extension
module.

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
