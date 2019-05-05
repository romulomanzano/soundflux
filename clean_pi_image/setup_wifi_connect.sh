#Add wifi-connect upon reboot
curl -L https://github.com/balena-io/wifi-connect/raw/master/scripts/raspbian-install.sh -O
chmod 777 raspbian-install.sh
nohup ./raspbian-install.sh -y
rm raspbian-install.sh
rm nohup.out
#create file so we can add to cron reboot
touch /home/pi/wifi-connect-start.sh
echo "iwgetid -r" >> /home/pi/wifi-connect-start.sh
echo "if [ $? -eq 0 ]; then" >> /home/pi/wifi-connect-start.sh
echo "    printf 'Skipping WiFi Connect\n'" >> /home/pi/wifi-connect-start.sh
echo "else" >> /home/pi/wifi-connect-start.sh
echo "    printf 'Starting WiFi Connect\n'" >> /home/pi/wifi-connect-start.sh
echo "    sudo wifi-connect --portal-ssid 'SoundFlux Home'" >> /home/pi/wifi-connect-start.sh
echo "fi" >> /home/pi/wifi-connect-start.sh
chmod 777 /home/pi/wifi-connect-start.sh
#add to crontab
( echo '@reboot sudo wifi-connect --portal-ssid "SoundFlux Home"' ) | crontab
#
sudo wifi-connect --portal-ssid 'SoundFlux Home'