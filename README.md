# extencli

A set of utilities around click, which offers extensible CLI mechanism, with little effort

## Features

### Easy third-party extensible click.group

This package offers a customized
[click.group](https://click.palletsprojects.com/en/stable/api/#click.Group)
definition, allowing one to quickly define a group of commands, which can be
extended by any package using the group defined thus. From thereon, simply
installing one's core module, and the third-party extension would automatically
extend the core's CLI with the third-party.

As an example, here is how one would define an extensible `click.group` in
their python package `core_module`:

```python
from extencli import PluginAutoloaderGroup

@click.group('core', cls=PluginAutoloaderGroup, depends_on='core_module', load_attr='cli_extension')
def core_group():
    ...
```

The `base_module` and `attribute_name` parameter are required to ensure that:
 - automated loading of the third-party packages will be done based on the dependency to `core_module`
 - third-party packages will be expected to provide a `cli_extension` function
   as their extension's entrypoint

Thus, a third party would merely need to do the following, in order for it to
be automatically loaded by the `core_module` auto-extension mechanism:

```python
from core_module.cli import core_group

@core_group.command('myext')
def cli_extension():
    ...
```

Now, by simply installing both the `core_module` and the `extension`
third-party, one would be able to observe that the `core_module`'s CLI was
extended with the `myext` command:

```shell
$> core --help
Usage: core [OPTIONS] COMMAND [ARGS]...

Options:
  --help                          Show this message and exit.

Commands:
  myext
```
