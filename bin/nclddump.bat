@ECHO OFF
:: Batch file to invoke nclddump Python script in MS-Windows
:: Written by Alex Ip 4/10/2016
:: Example invocation: nclddump.bat -h C:\Users\Alex\Downloads\sst.ltm.1971-2000_skos.nc --skos lang=pl altLabels=True narrower=True broader=True

setx PYTHONPATH ..\;%PYTHONPATH%

python -m nclddump %*