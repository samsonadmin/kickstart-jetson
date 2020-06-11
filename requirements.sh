#!/bin/bash

~/skip_sudo.sh
sudo apt-get update
sudo apt-get upgrade -y

## networking and modem

sudo snap install network-manager


sudo apt-get install libhdf5-serial-dev 

#This install a lot of need libs, might save other times before installing pip3 lib
sudo apt install -y \
   build-essential \
   cmake \
   pkg-config \
   libavcodec-dev \
   libavformat-dev \
   libswscale-dev \
   libssl1.0.0 \
   libgstreamer1.0-0 \
   gstreamer1.0-tools \
   libgstreamer1.0-dev \
   libgstreamer-plugins-base1.0-dev \
   gstreamer1.0-plugins-good \
   gstreamer1.0-plugins-bad \
   gstreamer1.0-plugins-ugly \
   gstreamer1.0-libav \
   libgstrtspserver-1.0-0 \
   libeigen3-dev \
   libglew-dev \
   libjpeg8-dev \
   liblapack-dev \
   liblapacke-dev \
   libopenblas-dev \
   libpostproc-dev \
   libtesseract-dev \
   libxine2-dev \
   libx264-dev \
   python-numpy \
   python3-dev \
   python3-pip \
   python3-numpy \
   python3-matplotlib \
   qv4l2 \
   v4l-utils \
   v4l2ucp \
   zlib1g-dev \
   libjansson4=2.11-1 \
   ffmpeg \
   curl \
   gawk \
   libhdf5-serial-dev \
   hdf5-tools \
   xdotool \
   libv4l-dev \
   libxvidcore-dev \
   libavresample-dev \
   python3-dev \
   libtbb2 \
   libtbb-dev \
   libtiff-dev \
   libjpeg-dev \
   libpng-dev \
   libtiff-dev \
   libdc1394-22-dev \
   libgtk-3-dev \
   libcanberra-gtk3-module \
   libatlas-base-dev \
   gfortran \
   wget \
   libgtk2.0-dev \
   unzip \
   v4l2ucp \
   python3-scipy \
   python3-pandas \
   python3-sympy \
   python-nose \
   libblas-dev \
   libprotobuf* \
   protobuf-compiler \
   ninja-build \
   python3-tk
   #gstreamer1.0-plugins-nice \
  

sudo apt-get update


sudo apt-get install libjpeg-dev zlib1g-dev

sudo -H pip install -U jetson-stats


#sudo systemctl set-default multi-user.target

sudo apt-get install -y ipython ipython-notebook 


sudo -H pip3 install -U pip testresources setuptools


sudo apt-get --with-new-pkgs upgrade
sudo apt autoremove -y
sudo apt-get dist-upgrade -y

sudo apt-get install nvidia-jetpack


#https://developer.ridgerun.com/wiki/index.php?title=Pose_Estimation_using_TensorRT_on_NVIDIA_Jetson

## For GPIO
sudo -H pip3 install Jetson.GPIO luma.led_matrix

## For SPI, https://github.com/gtjoseph/jetson-nano-support/tree/master
wget https://github.com/gtjoseph/jetson-nano-support/releases/download/v1.0.2/flash-dtb-update-2019-12-09.tar.gz
tar -zxvf flash-dtb-update-2019-12-09.tar.gz
