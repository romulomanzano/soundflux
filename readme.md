# Soundflux

Instructions for SoundFlux Deployment on a Raspberry Pi 3

## Using one of the pre-existing images

### Headless SoundFlux (Raspian)

The easiest way to get started is to flash the latest SoundFlux Pi image into a brand new SD card. 

#### Create Image Steps:
- Get the latest image from SoundFlux S3:
    - yyyy-mm-dd-sfx-wifi-enabled-raspian.img
- Flash into SD card using Balena Etcher:
    - https://www.balena.io/etcher/

This image is based on the latest (to date of img creation) version of Raspian with a couple of additions:

- Wifi-Connect enabled by default so it can be connected to a local network from any device
    - https://github.com/balena-io/wifi-connect
- The SoundFlux application already installed
    - Codebase available in the respective folders, not configured to run SoundFlux by default
#### Setup the image

- After flashing the image, insert the SD card into the Raspberry Pi 
- The device will open a wifi port so you can connect it to a local WLAN. From your phone, or computer, search for:
    - A wifi network called 'SoundFlux Home' and connect to it
    - It will take you to a sign-in page, where you can setup the wifi connection for the device
    
SSH is enabled for the device, however the credentials have been changed for security reason. Ask the SoundFlux team for details.

## Building Raspberry Image From Scratch

### Setup the Pi by itself:
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
 
### Setup for specific hardware configurations:
    * ./setup_pi.sh
    * ./setup_respeaker_4.sh

### Account Setup

Instructions TBD
