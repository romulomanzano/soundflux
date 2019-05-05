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
 * If you have the ReSpeaker 4, run the above (setup_pi.sh) and then this:
    * ./setup_respeaker_4.sh
 
 **Alternatively (recommended):** You can run both in the right order by simply running:
    
    * ./setup_pi_and_respeaker.sh

## Account Setup

Instructions TBD
