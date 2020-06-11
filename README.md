# Kickstart-Jetson
> Kickstart Jetson STEM Course
> Bootstraping the Jetson nano with Darknet Yolo


```bash
git clone https://github.com/samsonadmin/kickstart-jetson.git
cd kickstart-jetson
```

## Network Configure

```bash
./configure-network.sh
```
Create Wi-Fi hotspot 

|                |ASCII                      
|----------------|-------------------------------|
|SSID            |`i_am_jetson`          
|Password        |`jetsonnano`           


```bash
./requirements.sh
```

------

# GPIO
See [https://www.jetsonhacks.com/2019/06/07/jetson-nano-gpio/](https://www.jetsonhacks.com/2019/06/07/jetson-nano-gpio/)
See [https://github.com/NVIDIA/jetson-gpio](https://github.com/NVIDIA/jetson-gpio)


```bash
sudo -H pip3 install Jetson.GPIO luma.led_matrix

sudo groupadd -f -r gpio
sudo usermod -a -G gpio your_user_name
sudo usermod -a -G gpio jetsonnano

sudo cp /lib/udev/rules.d/60-jetson-gpio-common.rules  /etc/udev/rules.d/
sudo reboot
```

https://forums.developer.nvidia.com/t/read-write-permission-ttyths1/81623

created a udev rule: /etc/udev/rules.d/55-tegraserial.rules
KERNEL=="ttyTHS*", MODE="0666"
```bash
sudo /etc/rc.local
chmod 666 /dev/ttyTHS1
```


# Enable SPI on jetson nano

https://github.com/gtjoseph/jetson-nano-support/tree/l4t_32.2.1


## For SPI, https://github.com/gtjoseph/jetson-nano-support/tree/master

```bash
wget https://github.com/gtjoseph/jetson-nano-support/releases/download/v1.0.2/flash-dtb-update-2019-12-09.tar.gz
tar -zxvf flash-dtb-update-2019-12-09.tar.gz
```


# Using the max7219 matrix LED
```bash
pip install luma.led_matrix
```

# hardware:
https://raspi.tv/2013/8-x-8-led-array-driven-by-max7219-on-the-raspberry-pi-via-python

# Software:
https://github.com/rm-hull/luma.led_matrix


# Manage Autostart


Using Linux  **rc.local**
https://www.linuxbabe.com/linux-server/how-to-enable-etcrc-local-with-systemd
https://vpsfix.com/community/server-administration/no-etc-rc-local-file-on-ubuntu-18-04-heres-what-to-do/
```bash
sudo vim /etc/rc.local
#allow sending serial
if [ -f "/dev/ttyTHS1" ]; then
        chmod 666 /dev/ttyTHS1
fi

if [ -f "/dev/ttyUSB0" ]; then
        chmod 666 /dev/ttyUSB0
fi
```

# Finally
```bash
./start.sh
```

