#make sure necessary libraries are there
sudo apt-get install libasound2
sudo apt-get install libasound2-dev
#
mkdir ~/github/python_environments
mkdir ~/github/python_environments/falldetection
#create python virtual environment
python3 -m venv ~/github/python_environments/falldetection
source ~/github/python_environments/falldetection/bin/active
#install requirements
pip install requirements.txt