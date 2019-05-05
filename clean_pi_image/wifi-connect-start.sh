iwgetid -r
if [ $? -eq 0 ]; then
    printf 'Skipping WiFi Connect\n'
else
    printf 'Starting WiFi Connect\n'
    sudo wifi-connect --portal-ssid 'SoundFlux Home'
fi