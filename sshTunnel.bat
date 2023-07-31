@echo off
::
:: Simple Bat file so if ssh failes, we can get the output
::
echo Opening a Tunnel to server.  Once complete, open your browser
echo and use: 
echo          https://localhost:%2/jmx-console
echo to access.
ssh.exe -N -o ConnectTimeout=86400 -p 22 %1 -L %2:localhost:443

pause
exit
