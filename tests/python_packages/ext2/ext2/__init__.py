from test_core import core


@core.command('ext2-test')
def ext_test():
    print('Executing top-level subcommand')

@core.group('ext2')
def ext():
    print('Calling extension group')

@ext.command('test')
def test():
    print('Executing subcommand')
