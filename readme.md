# Soundflux

## Setup the Pi:
- Open a terminal (or ssh into your Pi)
- Create a directory called "/github/soundflux"
    * mkdir ~/github
    * mkdir ~/github/soundflux
    * cd ~/github/soundflux
* Clone the git repo into it:
    * git clone https://github.com/romulomanzano/soundflux.git ~/github/soundflux
* Go to that directory and run the setup_pi script:
    * cd ~/github/soundflux
    * chmod +x setup_pi.sh
    * ./setup_pi.sh
 * If you have the ReSpeaker 4, go to this link and configure it:
    * http://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/

## Setup a Windows Dev Env:
- Install git, vs c++ build tools,
- clone repo
- run setup_windows_dev.bat

## Publicly Available Datasets

### UrbanSounds8k spectrograms

All 8k audio files were converted to PNG using the logic described in "Transfer Learning Notebools/Transfer Learning - .wav to 2D MelSpectrogram to Png Files.ipynb" and made available here:
- https://s3.amazonaws.com/soundflux-urbansounds/kfold_spectrograms.zip
