#!/usr/bin/env python3

from distutils.core import setup
from sys import exit
import os, stat

'''
    Installation script that sets up NichePy and installs the modules it depends on.

    This should work on Unix-like systems including Cygwin on Windows. 
    
    To install:

    python3 setup.py install
'''


def setupFunc(): 
    print("\n Installing module nichefunc\n")
    setup(name='nichefdunc',
        version='1.1',
        description='Functions for estimating niche overlap and resampling species occurrence data',
        py_modules=['nichefunc'],
        author='Mariya Shcheglovitova, Bastian Bentlage',
        author_email='m.shcheglovitova@gmail.com, bastodian@gmail.com',
        url='http://purl.org/NichePy',
        license='GPL',
        )

def setupArg():
    print("\n Installing module argparse\n")
    setup(name='argparse',
        description='Module for writing user friendly command line interfaces',
        py_modules=['argparse'],
        author='Steven J. Bethard',
        author_email='steven.bethard@gmail.com',
        url='http://pypi.python.org/pypi/argparse',
        license='Python License',
        )

print("\nPlease choose your installation mode. Valid options are 1 or 2.\n\nIMPORTANT: Installation requires root privileges! Either change to the root account and run the script or use sudo.\n\n1 to make the scripts globally available. This will create symbolic links from the downloaded script files to /usr/bin.\n  In addition the module containing functions for NichePy will be installed using Python's installer.\n\n2 to install in the same manner as 2 but also install the argparse module using Python's installer.\n  This should only be necessary if you run Python3 < 3.2.\n\n")

### Ask for user input and create a list containing the python scripts to be installed
Install=input("\nPlease choose your installation mode: ")
Scripts=[os.path.join(os.getcwd(),x) for x in os.listdir(os.getcwd()) if "getMetric" in x or "nicheBack" in x or "nicheIdent" in x]

if int(Install)==1 or int(Install)==2:
    ### Where should the scripts be linked to?
    ExecPath=input("\nPlease type the path to which executables will be linked. If no entry default will be used (DEFAULT = /usr/bin): ")
    if len(ExecPath) == 0:
        ExecPath='/usr/bin'
    print('\nExecutable scripts will be linked to', ExecPath, 'to  make them globally avalilable on your system')
    ### Install option no 1
    if int(Install)==1:
        print("\nMaking scripts executable.")
        for file in Scripts:
            os.chmod(file, stat.S_IRWXU)
            NewFile=file.split('.')[0]
            Move='mv ' + file + ' ' + NewFile
            os.system(Move)
            Link='ln -s ' + file.split('.')[0] + ' ' + ExecPath
            os.system(Link)
        print("\nInstalling module nichefunc, which contains functions for executable NichePy scripts.")
        setupFunc()
        Rm='rm ' + 'nichefunc.py'
        os.system(Rm)
        Rm='rm ' + 'argparse.py'
        os.system(Rm)
        print("\nInstallation complete. Scripts can be called by issuing the following commands:")
        for i in os.listdir(os.getcwd()):
            if "getMetric" in i or "nicheBack" in i or "nicheIdent" in i:
                print("\n",i,"-h for brief guide of the script's usage")
    ### Install option no 2
    else:
        print("\nMaking scripts executable.")
        for file in Scripts:
            os.chmod(file, stat.S_IRWXU)
            NewFile=file.split('.')[0]
            Move='mv ' + file + ' ' + NewFile
            os.system(Move)
            Link='ln -s ' + file.split('.')[0] + ' ' + ExecPath
            os.system(Link)
        print("\nInstalling module nichefunc, which contains functions for executable NichePy scripts.")
        setupFunc()
        Rm='rm ' + 'nichefunc.py'
        os.system(Rm)
        setupArg()
        Rm='rm ' + 'argparse.py'
        os.system(Rm)
        print("\nInstallation complete. Scripts can be called by issuing the following commands:")
        for i in os.listdir(os.getcwd()):
            if "getMetric" in i or "nicheBack" in i or "nicheIdent" in i:
                print("\n",i,"-h for brief guide of the script's usage")
    print("\nFor more details please refer to the manual of NichePy.\n")
else:
    print("\nInvalid option entered. Please run installation script again!\n")
    exit()
