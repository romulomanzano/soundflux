# Soundflux

## Setup the Pi by itself:
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
    * ./setup_pi_and_respeaker.sh

 **Alternatively:** You can run each individual script by itself
    
    * ./setup_pi.sh
    * ./setup_respeaker_4.sh

## Account Setup

Instructions TBD
