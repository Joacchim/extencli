import click
from extencli import PluginAutoloaderGroup


@click.group('core', cls=PluginAutoloaderGroup, depends_on=['test-core', 'test_core'])
def core():
    ...
