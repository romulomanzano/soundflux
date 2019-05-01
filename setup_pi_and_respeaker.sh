#!/bin/bash
echo "======Setting up Python3.7.3======"
sh ./setup_python37.sh
echo "======Setting up SoundFlux application======"
sh ./setup_pi.sh
echo "======Setting up ReSpeaker Mic Array======"
sh ./setup_respeaker_4.sh