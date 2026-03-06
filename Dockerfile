FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget xvfb libgl1-mesa-dev python3 python3-pip \
    libx11-6 libglib2.0-0 libsodium-dev \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 \
    libxcb-xkb1 libxkbcommon-x11-0 libdbus-1-3 \
    curl net-tools git \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://downloads.coppeliarobotics.com/V4_7_0_rev4/CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04.tar.xz \
    && tar -xf CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04.tar.xz \
    && mv CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04 /opt/coppelia \
    && rm CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04.tar.xz

# Télécharger tous les fichiers Lua officiels de CoppeliaSim
# (inclut efficientConveyor_customization-3 et autres modules manquants)
RUN git clone https://github.com/CoppeliaRobotics/lua.git /tmp/coppelia_lua \
    && cp /tmp/coppelia_lua/*.lua /opt/coppelia/lua/ \
    && rm -rf /tmp/coppelia_lua

ENV COPPELIASIM_ROOT=/opt/coppelia
ENV LD_LIBRARY_PATH=/opt/coppelia
ENV QT_QPA_PLATFORM=offscreen

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]