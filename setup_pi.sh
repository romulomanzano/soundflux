#make sure necessary libraries are there
sudo apt install libblas-dev llvm
sudo apt install vim
sudo apt-get install libatlas-base-dev
sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024
sudo /sbin/mkswap /var/swap.1
sudo chmod 600 /var/swap.1
sudo /sbin/swapon /var/swap.1
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
#Revert extra swap
sudo swapoff /var/swap.1
sudo rm /var/swap.1
