import os
import sys
import re
import filecmp
import time
import tomllib
import subprocess
import platform
import numpy as np
from io import StringIO
from pathlib import Path
from numpy.testing import assert_array_equal, assert_almost_equal, assert_allclose

PROGS_PATH = Path(f'dist/CFML/progs').resolve()


# Help functions

def set_crysfml_db_path():
    """Sets the env variable 'CRYSFML_DB' as the path to the 'Databases' directory containing the file 'magnetic_data.txt'."""
    default = os.path.join(os.getcwd(), '..', '..', '..')
    project_dir = os.getenv('GITHUB_WORKSPACE', default=default)  # locally do: export GITHUB_WORKSPACE=`pwd`
    config_path = os.path.join(project_dir, 'scripts.toml')
    with open(config_path, 'rb') as f:
        CONFIG = tomllib.load(f)
    repo_dir = CONFIG['cfml']['dir']['repo']
    src_dir = CONFIG['cfml']['dir']['repo-src']
    db_path = os.path.join(project_dir, repo_dir, src_dir, 'Databases')
    os.environ['CRYSFML_DB'] = db_path

def change_cwd_to_tests():
    """Changes the current directory to the directory of this script file."""
    os.chdir(os.path.dirname(__file__))

def run_exe_with_args(file_name:str, args:str=''):
    """Runs the executable with optional arguments."""
    if platform.system() == 'Windows':
        file_name = f'{file_name}.exe'
    exe_path = os.path.join(PROGS_PATH, file_name)
    cmd = f'{exe_path}'
    if args:
        cmd = f'{exe_path} {args}'
    #os.system(f"echo '::::: {cmd}'")
    os.system(f'{cmd}')
    time.sleep(1)

def dat_to_ndarray(file_name:str, skip_begin:int=3, skip_end:int=4):
    """Parses the file to extract an array of data and converts it to a numpy array."""
    with open(file_name, 'r') as file:
        lines = file.readlines()  # reads into list
    del lines[:skip_begin]  # deletes requested number of first lines
    del lines[len(lines)-skip_end:]  # deletes requested number of last lines
    lines = [l.replace('(',' ').replace(')', ' ') for l in lines]  # replace brackets with spaces
    joined = '\n'.join(lines)  # joins into single string
    data = np.genfromtxt(StringIO(joined), usecols=(1, 2, 3, 4, 5, 6, 7))  # converts string to ndarray
    return data

# Set up paths

change_cwd_to_tests()
set_crysfml_db_path()

# Tests

def test__Bond_StrN__LiFePO4n():
    run_exe_with_args('Bond_StrN', args='LiFePO4n.cfl')
    desired = dat_to_ndarray('LiFePO4n_sum_desired.bvs')
    actual = dat_to_ndarray('LiFePO4n_sum.bvs')
    assert_allclose(desired, actual, rtol=1e-02, verbose=True)


# Debug

if __name__ == '__main__':
    #os.system(f"echo '::::: ls -l'")
    #os.system(f'ls -l')
    test__Bond_StrN__LiFePO4n()
