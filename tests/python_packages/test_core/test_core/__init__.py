import click
from extencli import PluginAutoloaderGroup


@click.group('core', cls=PluginAutoloaderGroup, depends_on=['test-core', 'test_core'], load_attr='ext')
def core():
    ...
