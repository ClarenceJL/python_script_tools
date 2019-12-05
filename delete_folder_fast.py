"""
A fast way to delete a folder recursively containing a large amount of files using perl
Author: Claire Li
Reference: 
https://unix.stackexchange.com/questions/37329/efficiently-delete-large-directory-containing-thousands-of-files
"""

import subprocess as sp
import os


def delete_folder_recursive(path, depth, delete_current_folder=True):
    if depth > 0:
        prefix = '  '*(depth-1) + '|' +'_'
    else:
        prefix = ''
    print(prefix + 'deleting (sub)directory ' + path)
    file_list = []
    for pname in os.listdir(path):
        child_path = path + '/' + pname
        if os.path.isdir(child_path):
            delete_folder_recursive(child_path, depth+1)
        else:
            file_list.append(child_path)

    # delete files in current folder
    sp.call(["perl", "-e", " \'for(<*>){((stat)[9]<(unlink))}\'"])
    if delete_current_folder:
        sp.call(["rm", "-rf", path])


if __name__ == "__main__":
    path=input('Please input folder directory to be deleted: ')
    path_ensure = input('Please input folder directory again to confirm: ')
    assert path == path_ensure, 'Error: the folder names you input are different!'
    assert os.path.exists(path), 'Error: '+path+' is not a valid directory!'
 
    ans = input('Are you sure you want to delete everything in folder {} [y/n]: '.format(path))
    if ans == 'y' or ans =='yes':
        delete_folder_recursive(path, 0)
        print('Done.')
    else:
        print('Exit program.')
    




