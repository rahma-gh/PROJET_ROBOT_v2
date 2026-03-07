#!/bin/bash
set -e

echo "=== Starting CoppeliaSim (headless) ==="

xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' \
  /opt/coppelia/coppeliaSim \
    -h \
    -s 600000 \
    -G zmqRemoteApi.rpcPort=23000 \
    /app/pick_and_place.ttt > coppeliasim.log 2>&1 &

COPPELIA_PID=$!

echo "=== Waiting for ZMQ server to be fully ready ==="
TIMEOUT=60
ELAPSED=0
while ! grep -q "ZMQ remote API server" coppeliasim.log 2>/dev/null; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ $ELAPSED -gt $TIMEOUT ]; then
        echo "TIMEOUT: CoppeliaSim n'a pas démarré à temps"
        cat coppeliasim.log
        exit 1
    fi
    echo "  waiting... ${ELAPSED}s"
done

echo "ZMQ server detected. Waiting 5s for scene loading..."
sleep 5

echo "=== Running pytest ==="
export PYTHONPATH=/app
pytest tests/test_regression.py \
    --html=report.html \
    --self-contained-html \
    --timeout=60 \
    -vv

TEST_EXIT_CODE=$?

kill -TERM $COPPELIA_PID 2>/dev/null || true
exit $TEST_EXIT_CODE