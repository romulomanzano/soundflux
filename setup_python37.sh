sudo apt-get update -y
sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev -y
#download & install python3
wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz
tar xf Python-3.7.3.tar.xz
cd Python-3.7.3
./configure
make -j 4
sudo make altinstall
#clean stuff
cd ..
sudo rm -r Python-3.7.3
rm Python-3.7.3.tar.xz
#check versions
python3.7 --version
pip3.7 --version