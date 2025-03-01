import sys
import argparse
import os
sys.path.append(os.getcwd())
try:
    import _yadata_types
except ModuleNotFoundError as mnfe:
    if mnfe.name=='_yadata_types':
        pass
    else:
        raise

import yadata.command
import yadata.utils.sane_yaml as sane_yaml

c_map={
    'read':yadata.command.Read,
    'append':yadata.command.Append,
    'filter':yadata.command.Filter,
    'exec':yadata.command.Exec,
    'merge':yadata.command.Merge,
    'sort':yadata.command.Sort,
    'render':yadata.command.Render,
    'type':yadata.command.Type,
    'cast':yadata.command.Cast,
    'run':yadata.command.Run,
    'yield':yadata.command.Yield,
}

def run():
    parse=argparse.ArgumentParser()
    subparsers=parse.add_subparsers(dest='command',help='The yadata subcommand you want to run')
    subparsers.required=True
    for cmd in c_map:
        cmd_class=c_map[cmd]
        subpar=subparsers.add_parser(cmd,help=cmd_class.__doc__,description=cmd_class.__doc__)
        cmd_class.add_arguments(subpar)

    argv_splitted=[]
    subcommand_argv=[]
    for arg in sys.argv[1:]:
        if arg=='!':
            argv_splitted.append(subcommand_argv)
            subcommand_argv=[]
        else:
            subcommand_argv.append(arg)
    argv_splitted.append(subcommand_argv)
    it=None
    for i,subcommand_argv in enumerate(argv_splitted):
        ns=parse.parse_args(subcommand_argv)
        command=c_map[ns.command](ns)
        if i==0 and command.data_in:
            it=sane_yaml.load_all(sys.stdin)        
        if command.data_in:
            if it is None:
                raise ValueError(f'subcommand {ns.command} without input data')
            it=command.execute(it)
        else:
            it=command.execute()
    if command.data_out:
        for rec in it:
            sys.stdout.write('---\n')
            sys.stdout.write(sane_yaml.dump(rec))

