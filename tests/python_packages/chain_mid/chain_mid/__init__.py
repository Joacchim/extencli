from chain_core import chain
from extencli import PluginAutoloaderGroup


@chain.group('mid', cls=PluginAutoloaderGroup, depends_on='chain-mid')
def mid():
    ...


__all__ = ['mid']
