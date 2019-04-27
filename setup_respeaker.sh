sudo apt-get update
sudo apt-get upgrade
#create re-speaker folder
mkdir ~/github/respeaker
git clone https://github.com/respeaker/seeed-voicecard.git ~/github/respeaker
cd ~/github/respeaker/seeed-voicecard
sudo ./install.sh
amixer cset numid=3 1
sudo reboot now