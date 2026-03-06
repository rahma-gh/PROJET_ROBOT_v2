# ===============================
# Base Image
# ===============================
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# ===============================
# System Dependencies
# ===============================
RUN apt-get update && apt-get install -y \
    wget \
    xvfb \
    libgl1-mesa-dev \
    libgl1-mesa-glx \
    python3 \
    python3-pip \
    python3-dev \
    libx11-6 \
    libglib2.0-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libfontconfig1 \
    libfreetype6 \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ===============================
# Install CoppeliaSim 4.1.0
# (seule version supportée par PyRep)
# ===============================
RUN wget https://www.coppeliarobotics.com/files/CoppeliaSim_Edu_V4_1_0_Ubuntu20_04.tar.xz \
    && tar -xf CoppeliaSim_Edu_V4_1_0_Ubuntu20_04.tar.xz \
    && mv CoppeliaSim_Edu_V4_1_0_Ubuntu20_04 /opt/coppelia \
    && rm CoppeliaSim_Edu_V4_1_0_Ubuntu20_04.tar.xz

ENV COPPELIASIM_ROOT=/opt/coppelia
ENV LD_LIBRARY_PATH=$COPPELIASIM_ROOT:$LD_LIBRARY_PATH
ENV QT_QPA_PLATFORM_PLUGIN_PATH=$COPPELIASIM_ROOT
ENV QT_QPA_PLATFORM=offscreen

# ===============================
# Install PyRep
# ===============================
RUN git clone https://github.com/stepjam/PyRep.git /opt/pyrep \
    && cd /opt/pyrep \
    && pip3 install -r requirements.txt \
    && pip3 install .

# ===============================
# Workdir + Python Dependencies
# ===============================
WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# ===============================
# Copy Project
# ===============================
COPY . .

# ===============================
# Entrypoint — pytest directement
# Plus besoin de script bash complexe :
# PyRep lance CoppeliaSim en interne
# ===============================
CMD ["python3", "-m", "pytest", "tests/", \
     "--html=report.html", \
     "--self-contained-html", \
     "--timeout=180", \
     "-vv"]