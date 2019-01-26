#make sure necessary libraries are there
sudo apt-get install libasound2
# in ubuntu you may need to install via aptitude and downgrade sudo apt-get install aptitude
sudo apt-get install libasound2-dev
sudo apt install libblas-dev llvm
sudo apt install vim
sudo apt-get install libatlas-base-dev
#install virtualenv
sudo pip3 install virtualenv
#
mkdir ~/github/python_environments
mkdir ~/github/python_environments/falldetection
#create python virtual environment
python3 -m venv ~/github/python_environments/falldetection
source ~/github/python_environments/falldetection/bin/activate
#install requirements
pip3 install -r requirements.txt