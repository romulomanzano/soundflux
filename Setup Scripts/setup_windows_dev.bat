mkdir %HOMEDRIVE%%HOMEPATH%\Documents\GitHub\python_environments
mkdir %HOMEDRIVE%%HOMEPATH%\Documents\GitHub\python_environments\soundflux
python -m venv %HOMEDRIVE%%HOMEPATH%\Documents\GitHub\python_environments\soundflux
call %HOMEDRIVE%%HOMEPATH%\Documents\GitHub\python_environments\soundflux\scripts\activate.bat
pip3 install --upgrade pip --user
pip3 install -r %HOMEDRIVE%%HOMEPATH%\Documents\GitHub\soundflux\requirements.txt --user
ECHO "COMPLETE!"
PAUSE