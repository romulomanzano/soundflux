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