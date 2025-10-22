from test_core import core


@core.group('ext2')
def ext():
    print('Calling extension group')

@ext.command('test')
def test():
    print('Executing subcommand')
