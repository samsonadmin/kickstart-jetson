#!/bin/bash

~/skip_sudo.sh
sudo apt-get update
sudo apt-get upgrade -y

## networking and modem
sudo snap install modem-manager
sudo snap install network-manager

## should install Pytorch and tensorflow 1st
## Download from https://developer.nvidia.com/embedded/downloads

https://forums.developer.nvidia.com/t/pytorch-for-jetson-nano-version-1-5-0-now-available/72048
sudo apt-get install python3-pip libopenblas-base libopenmpi-dev 
pip3 install Cython
pip3 install numpy torch-xxxxx

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

pip3 install tensorflow--xxxx
sudo apt-get install libhdf5-serial-dev 
pip3 install tensorflow--xxxx


## Torchvision
#PyTorch v1.3 - torchvision v0.4.2
#PyTorch v1.4 - torchvision v0.5.0
#PyTorch v1.5 - torchvision v0.6.0

sudo apt-get install libjpeg-dev zlib1g-dev
git clone --branch v0.6.0 https://github.com/pytorch/vision torchvision
cd torchvision
sudo python3 setup.py install
cd ../


##for opencv 4
#dependencies=(build-essential cmake pkg-config libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libavresample-dev python3-dev libtbb2 libtbb-dev libtiff-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev libgtk-3-dev libcanberra-gtk3-module libatlas-base-dev gfortran wget unzip)

#sudo apt install -y ${dependencies[@]}


#sudo systemctl set-default multi-user.target

#sudo apt-get install -y ipython ipython-notebook 


sudo -H pip3 install -U pip testresources setuptools

#sudo pip3 install -U numpy==1.16.1 future==0.17.1 mock==3.0.5 h5py==2.9.0 keras_preprocessing==1.0.5 keras_applications==1.0.8 gast==0.2.2 futures protobuf pybind11

sudo -H pip3 install keras h5py matplotlib pandas

sudo -H pip3 install -U testresources setuptools numpy future mock h5py keras gast futures protobuf pybind11 grpcio absl-py py-cpuinfo psutil portpicker six mock requests gast h5py astor termcolor protobuf wrapt google-pasta pandas

## -U (meaning upgrade)

##for onnx
sudo apt-get install -y protobuf-compiler libprotoc-dev
sudo apt-get install -y libprotobuf* protobuf-compiler ninja-build

sudo -H pip3 install onnx==1.4.1

sudo -H pip3 install pycuda
sudo -H pip3 install Pillow

##for trt_pos
sudo -H pip3 install --upgrade cython
sudo -H pip3 install tqdm cython pycocotools
sudo -H pip3 install 'pillow<7'


#sudo dpkg -i OpenCV-4.1.1-dirty-aarch64-*.deb

sudo apt-get --with-new-pkgs upgrade
sudo apt autoremove -y
sudo apt-get dist-upgrade -y


## for https://gitlab.com/StrangeAI/centernet_pro_max
sudo -H pip3 install tabulate cloudpickle imagesize portalocker easydict skimage


#scikit-image takes long imte
#for StrangeAI/first_order_transfer
sudo -H pip3 install imageio
sudo -H pip3 install scikit-image

sudo -H pip3 install sklearn
sudo apt install -y python3-decorator

sudo apt install -y lexnlp


sudo apt-get install nvidia-jetpack


#https://developer.ridgerun.com/wiki/index.php?title=Pose_Estimation_using_TensorRT_on_NVIDIA_Jetson

## For GPIO
sudo -H pip3 install Jetson.GPIO luma.led_matrix

## For SPI, https://github.com/gtjoseph/jetson-nano-support/tree/master
wget https://github.com/gtjoseph/jetson-nano-support/releases/download/v1.0.2/flash-dtb-update-2019-12-09.tar.gz
tar -zxvf flash-dtb-update-2019-12-09.tar.gz
