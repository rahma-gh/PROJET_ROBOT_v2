#!/bin/bash
set -e

echo "=== Starting CoppeliaSim (headless) ==="

# On lance CoppeliaSim
xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' \
  /opt/coppelia/coppeliaSim \
    -h \
    -G zmqRemoteApi.rpcPort=23000 \
    /app/pick_and_place.ttt > coppeliasim.log 2>&1 &

COPPELIA_PID=$!

echo "=== Waiting for ZMQ server to be fully ready ==="
# On attend que le log confirme que le serveur est prêt
TIMEOUT=60
ELAPSED=0
while ! grep -q "ZMQ remote API server" coppeliasim.log; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ $ELAPSED -gt $TIMEOUT ]; then
        echo "TIMEOUT: CoppeliaSim n'a pas démarré à temps"
        cat coppeliasim.log
        exit 1
    fi
    echo "  waiting... ${ELAPSED}s"
done

# CRUCIAL : On attend encore 5 secondes pour que la scène .ttt soit chargée
echo "ZMQ server detected. Waiting 5s for scene loading..."
sleep 5

echo "=== Running pytest ==="
pytest tests/test_regression.py --html=report.html --self-contained-html