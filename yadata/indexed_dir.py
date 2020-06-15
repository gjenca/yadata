
import os
import shelve

class DirObject:

    def __init__(self,files,dirs,dir_fd):
        self.mtimed_files={}
        self.dirs_set=set(dirs)
        for name in files:
            if not name.startswith('.'):
                self.mtimed_files[name]=os.stat(name,dir_fd=dir_fd).st_mtime

def deepscan_dir(dirname,crud_object,indexfile=None):

        if not indexfile:
            indexfile=os.path.join(dirname,'.index.db')
        index=shelve.open(indexfile)
        for root,dirs,files,dir_fd in os.fwalk(dirname):
            root=root[len(dirname):]
            current_state=DirObject(files,dirs,dir_fd)
            if root not in index:
                previous_state=DirObject([],[],None)
            else:
                previous_state=index[root]
            # deleted files
            for name in previous_state.mtimed_files.keys()-current_state.mtimed_files.keys():
                crud_object.delete(os.path.join(root,name))
            # created files
            for name in current_state.mtimed_files.keys()-previous_state.mtimed_files.keys():
                crud_object.create(os.path.join(root,name))
            # updated files
            for name in current_state.mtimed_files:
                if name in previous_state.mtimed_files and \
                    previous_state.mtimed_files[name]!=current_state.mtimed_files[name]:
                    crud_object.update(os.path.join(root,name))
            # deleted dirs (TODO: recursively)
            roots_to_delete=[]
            for dirname in previous_state.dirs_set-current_state.dirs_set:
                prefix=dirname
                for root_dirname,dirobject in index.items():
                    if root_dirname.startswith(prefix):
                        for name in dirobject.mtimed_files:
                            crud_object.delete(os.path.join(root_dirname,name))
                        roots_to_delete.append(root_dirname)
            for root_dirname in roots_to_delete:
                del index[root_dirname]
            index[root]=current_state
        index.close()

