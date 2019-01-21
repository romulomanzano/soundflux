#make sure necessary libraries are there
sudo apt-get install libasound2
sudo apt-get install libasound2-dev
#
mkdir ~/github
mkdir ~/github/falldetection
mkdir ~/github/python_environments
mkdir ~/github/python_environments/falldetection
#pull from git
git clone https://github.com/romulomanzano/falldetection.git ~/github/falldetection
#create python virtual environment
python3 -m venv ~/github/python_environments/falldetection
source ~/github/python_environments/falldetection/bin/active
#install requirements
pip install requirements.txt