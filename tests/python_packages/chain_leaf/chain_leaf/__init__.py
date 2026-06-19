from chain_core import chain
from chain_mid import mid


@chain.command('leaf-deep')
def leaf_deep():
    print('Executing leaf top-level command')


@mid.command('leafcmd')
def leafcmd():
    print('Executing leaf mid-level subcommand')
