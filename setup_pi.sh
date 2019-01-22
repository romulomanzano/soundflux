#make sure necessary libraries are there
sudo apt-get install libasound2
sudo apt-get install libasound2-dev
sudo apt install libblas-dev
sudo apt-get install llvm
#install virtualenv
sudo pip3 install virtualenv
#
mkdir ~/github/python_environments
mkdir ~/github/python_environments/falldetection
#create python virtual environment
python3 -m venv ~/github/python_environments/falldetection --without-pip
source ~/github/python_environments/falldetection/bin/activate
#install requirements
pip3 install -r requirements.txt --user