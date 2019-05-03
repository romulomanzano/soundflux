# increase swap space, this is good practice but also needed to install scipy
sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024
sudo /sbin/mkswap /var/swap.1
sudo /sbin/swapon /var/swap.1
#make sure necessary libraries are there
sudo apt-get install libasound2
# in ubuntu you may need to install via aptitude and downgrade sudo apt-get install aptitude
sudo apt-get install libasound2-dev
sudo apt-get install libhdf5-serial-dev
sudo apt install libblas-dev llvm
sudo apt install vim
sudo apt-get install zip
sudo apt-get install sox
sudo apt-get install libatlas-base-dev
#create virtual environment
mkdir ~/github/python_environments
mkdir ~/github/python_environments/soundflux
#create python virtual environment
python3.7 -m venv ~/github/python_environments/soundflux
source ~/github/python_environments/soundflux/bin/activate
#install requirements
pip install --upgrade pip
pip install -r requirements_pi.txt