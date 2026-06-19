import os

import click

from extencli import PluginAutoloaderGroup

# The eager-load behaviour is toggled through an environment variable so the
# same installed chain can be exercised in both modes by the test harness.
_EAGER = os.environ.get('EXTENCLI_EAGER', '1') != '0'


@click.group('chain', cls=PluginAutoloaderGroup, depends_on='chain-core', eager_load=_EAGER)
def chain():
    ...
