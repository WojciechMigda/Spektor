FROM ubuntu:16.04

# Update OS
RUN sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y upgrade

# Install Python
RUN apt-get install -y python3-dev python3-pip python3-flask python3-jsonschema python3-skimage python3-requests
# Install tools
RUN apt-get install -y git cmake sudo wget


RUN mkdir -p /webapp

# Set the default directory for our environment
ENV HOME /webapp/service
WORKDIR /webapp/service
RUN mkdir -p /webapp/service/.luarocks

# Add requirements.txt
ADD requirements.txt /webapp


### OPENCV
RUN git clone --depth 1 https://github.com/opencv/opencv.git && cd opencv && mkdir build && cd build && cmake ../ && make -j 8 && make install && make clean && cd ../..


### TORCH
RUN git clone --depth 1 https://github.com/torch/distro.git torch --recursive && cd torch && bash install-deps && ./install.sh cd ..

ENV PATH=/webapp/service/torch/install/bin:$PATH

RUN luarocks install dpnn

ENV LUA_PATH=$HOME'/.luarocks/share/lua/5.1/?.lua':$HOME'/.luarocks/share/lua/5.1/?/init.lua':$HOME'/torch/install/share/lua/5.1/?.lua':$HOME'/torch/install/share/lua/5.1/?/init.lua;./?.lua':$HOME'/torch/install/share/luajit-2.1.0-beta1/?.lua;/usr/local/share/lua/5.1/?.lua;/usr/local/share/lua/5.1/?/init.lua'
ENV LUA_CPATH=$HOME'/.luarocks/lib/lua/5.1/?.so':$HOME'/torch/install/lib/lua/5.1/?.so;./?.so;/usr/local/lib/lua/5.1/?.so;/usr/local/lib/lua/5.1/loadall.so'
ENV LD_LIBRARY_PATH=$HOME/torch/install/lib:$LD_LIBRARY_PATH
ENV DYLD_LIBRARY_PATH=$HOME/torch/install/lib:$DYLD_LIBRARY_PATH
ENV LUA_CPATH=$HOME'/torch/install/lib/?.so;'$LUA_CPATH



### /webapp/service/torch/install/bin/torch-activate

# Install app requirements
RUN pip3 install -r /webapp/requirements.txt


### OPENFACE
RUN git clone https://github.com/cmusatyalab/openface.git && cd openface && python3 setup.py install

# Create app directory
ADD ./src /webapp

# Expose port 5000
EXPOSE 5000 5000

ENTRYPOINT ["python3", "/webapp/service/main.py", "--app-host", "0.0.0.0", "-V"]
