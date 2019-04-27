# Soundflux

## Setup the Pi:
- Open a terminal (or ssh into your Pi)
- Install git:
   * sudo apt-get install git
- Create a directory called "/github/soundflux"
    * mkdir ~/github
    * mkdir ~/github/soundflux
* Clone the git repo into it:
    * git clone -b sfx-edge-pi --single-branch --depth 1 https://github.com/romulomanzano/soundflux.git ~/github/soundflux
* Go to that directory and run the setup_pi script:
    * cd ~/github/soundflux
    * chmod +x setup_pi.sh
    * ./setup_pi.sh
 
## Setup for specific hardware configurations:
 * If you have the ReSpeaker 4, go to this link and configure it:
    * http://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/
