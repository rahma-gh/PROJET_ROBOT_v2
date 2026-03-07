FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget xvfb libgl1-mesa-glx libgl1-mesa-dri python3 python3-pip \
    libx11-6 libglib2.0-0 libsodium-dev \
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 \
    libxcb-xkb1 libxkbcommon-x11-0 libdbus-1-3 \
    libxrender1 libxi6 libxext6 \
    netcat-openbsd curl net-tools git \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://downloads.coppeliarobotics.com/V4_7_0_rev4/CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04.tar.xz \
    && tar -xf CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04.tar.xz \
    && mv CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04 /opt/coppelia \
    && rm CoppeliaSim_Edu_V4_7_0_rev4_Ubuntu22_04.tar.xz

# NOTE: Do NOT overwrite /opt/coppelia/lua/ with the GitHub repo.
# The CoppeliaRobotics/lua repo targets a different version and corrupts
# sim-1.lua, breaking all add-ons (including the ZMQ server).
# The .ttt scene file provides any custom Lua it needs at runtime.

ENV COPPELIASIM_ROOT=/opt/coppelia
ENV LD_LIBRARY_PATH=/opt/coppelia
# Use xcb (X11) platform so CoppeliaSim's internal Qt/GUI layer initialises
# correctly under Xvfb. The 'offscreen' platform skips parts of the GUI
# bootstrap that CoppeliaSim v4.7 requires before it can start add-ons.
ENV QT_QPA_PLATFORM=xcb

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]