#/bin/bash 

clear

sudo apt-get update
sudo apt-get install v4l-utils
sudo apt-get install gawk
sudo apt-get install curl

#sudo snap install modem-manager
sudo snap install network-manager


##Create WiFi Hotspot connection
#https://gist.github.com/narate/d3f001c97e1c981a59f94cd76f041140

#sudo nmcli connection down jetson_hotspot

sudo nmcli connection delete jetson_hotspot


sudo nmcli connection add type wifi ifname '*' con-name jetson_hotspot autoconnect no ssid i_am_jetson


sudo nmcli connection modify jetson_hotspot 802-11-wireless.mode ap 
sudo nmcli connection modify jetson_hotspot 802-11-wireless.channel 11 802-11-wireless.band bg 


sudo nmcli connection modify jetson_hotspot 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk jetsonnano

##sudo nmcli con modify jetson_hotspot 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared

#nmcli con modify jetson_hotspot wifi-sec.key-mgmt wpa-psk
#nmcli con modify jetson_hotspot wifi-sec.psk "car1hkcar1hk"

#sudo nmcli connection modify jetson_hotspot 802-11-wireless-security.proto rsn
#sudo nmcli connection modify jetson_hotspot 802-11-wireless-security.group ccmp
#sudo nmcli connection modify jetson_hotspot 802-11-wireless-security.pairwise ccmp

sudo nmcli connection modify jetson_hotspot ipv4.address 192.168.2.1/24
sudo nmcli connection modify jetson_hotspot ipv4.method shared

#need to restart network manager becaused you changed IP address
sudo systemctl restart NetworkManager

sleep 2
#Last step
sudo nmcli connection up jetson_hotspot
sudo nmcli connection modify jetson_hotspot connection.autoconnect yes

sleep 1

sudo nmcli device wifi list
sudo nmcli dev show wlan0


##create mobile connections
## It takes time for usb_switch to work internally
## If you reset the connection, it will takes around a min seconds (tested 47s) to reconnect to the network, so please be patient and wait
sleep 2





#If after reboot nmcli con up Hotspot doesn't work
#Use this command instead to start Hotspot
#UUID=$(grep uuid /etc/NetworkManager/system-connections/Hotspot | cut -d= -f2)
#nmcli con up uuid $UUID


#sudo iw dev wlan0 set power_save off

##Show info
#nmcli -p -f general,wifi-properties device show wlan0

##Extra
#GUI tool, accessible from remote X11
#nm-connection-editor