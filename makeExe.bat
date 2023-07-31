::@echo off

::
:: This file will create an executable out of the required files
::

:: Make sure to flush dist directory
rd /S /Q dist
rd /S /Q build

:: Clean anything
::pyinstaller --clean UmDbSpy.py

:: Finally call the pyinstaller to create the package
::pyinstaller --windowed UmDbSpy.py --icon=spyvsspy-icon.ico
pyinstaller --console UmDbSpy.py --icon=spyvsspy-icon.ico 

:: Copy the images to the directory
mkdir dist\UmDbSpy\images
xcopy images dist\UmDbSpy\images /y

:: Copy the Graphviz executable over
mkdir dist\UmDbSpy\Graphviz
xcopy Graphviz dist\UmDbSpy\Graphviz /E /y

:: Copy the spy vs spy icon
copy spyvsspy-icon.gif dist\UmDbSpy
copy spyvsspy-icon.ico dist\UmDbSpy

:: Copy the sqlite executable
copy sqlite3.exe dist\UmDbSpy

:: Copy the ssh and other items required
copy ssh.exe dist\UmDbSpy
copy ssh.bat dist\UmDbSpy
copy sshTunnel.bat dist\UmDbSpy
copy "cygcom_err-2.dll" dist\UmDbSpy
copy "cygcrypto-1.0.0.dll" dist\UmDbSpy
copy "cyggcc_s-1.dll" dist\UmDbSpy
copy "cyggssapi_krb5-2.dll" dist\UmDbSpy
copy "cygiconv-2.dll" dist\UmDbSpy
copy "cygintl-8.dll" dist\UmDbSpy
copy "cygk5crypto-3.dll" dist\UmDbSpy
copy "cygkrb5-3.dll" dist\UmDbSpy
copy "cygkrb5support-0.dll" dist\UmDbSpy
copy "cygssp-0.dll" dist\UmDbSpy
copy "cygwin1.dll" dist\UmDbSpy
copy "cygz.dll" dist\UmDbSpy

:: Copy the 7zip files over
copy "7z.dll" dist\UmDbSpy
copy "7z.exe" dist\UmDbSpy
copy "7z.sfx" dist\UmDbSpy
copy "7zCon.sfx" dist\UmDbSpy
copy "7-zip.dll" dist\UmDbSpy

:: Copy the mathplot lib data
::mkdir dist\UmDbSpy\mpl-data
::xcopy mpl-data dist\UmDbSpy\mpl-data

:: Copy the scripts data
mkdir dist\UmDbSpy\scripts
xcopy scripts dist\UmDbSpy\scripts




