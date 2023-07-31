The OPM DB Spy is a simple python GUI that talks to an OPM database.  For
more information please see the wiki page:

        https://wikid.netapp.com/w/MEG/OPM/Engineering/Development/OPMDbSpy

If you want to be able to develop and build it, you will need to have these 
dependencies installed on your computer (make sure to download the correct
version so either 32 or 64 bit):

	o - Python 2.7 : http://www.python.org/downloads/
	o - WX Python (for 2.7) : http://www.wxpython.org/download.php
	o - Python MySqldb : http://sourceforge.net/projects/mysql-python/
	o - Python Numeric : http://sourceforge.net/projects/numpy/files/OldFiles/
               For the 64 bit binary goto here http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
	o - Python Pydot : https://pypi.python.org/pypi/pydot
               Download the tar.gz, extract and run "python setup.py install"
	o - Python Matplotlib : http://matplotlib.org/downloads.html
        o - Python Setup Tools: https://pypi.python.org/pypi/setuptools#windows
               Download the ez_setup.py and run "python ez_setup.py"
	o - Python DateUtil : https://pypi.python.org/pypi/python-dateutil
               Download the tar.gz, extract and run "python setup.py install"
	o - Python Parsing : https://pypi.python.org/pypi/pyparsing/1.5.7#downloads
        o - Python Secure FTP : https://code.google.com/p/pysftp/downloads/list
               (There will be some errors but you can ignore those.)
	o - Python Crypto : http://www.voidspace.org.uk/python/modules.shtml#pycrypto
               Download the binary distribution created with MS Visual Studio
	o - Python For Windows Extension : http://sourceforge.net/projects/pywin32/files/pywin32/
	o - Python Installer : http://www.pyinstaller.org/
               Download the zip, extract and run "python setup.py install"
               (Need to add C:\python27\scripts to the PATH env)

Finally if you are having issues with any packages, you can usually find the
binaries here:
	http://www.lfd.uci.edu/~gohlke/pythonlibs/



Once you have all of these installed, you can run the makeExe.bat file which will
create a "dist" directory of the executable, or you can just call:

        python OpmDbSpy.py


