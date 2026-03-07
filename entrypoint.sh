#!/bin/bash
set -e

echo "=== Starting Xvfb ==="
Xvfb :99 -screen 0 1024x768x24 &
XVFB_PID=$!
export DISPLAY=:99
sleep 1

echo "=== Starting CoppeliaSim (headless, DISPLAY=$DISPLAY) ==="
/opt/coppelia/coppeliaSim \
    -h \
    -s 600000 \
    -G zmqRemoteApi.rpcPort=23000 \
    /app/pick_and_place.ttt > coppeliasim.log 2>&1 &

COPPELIA_PID=$!

echo "=== Waiting for ZMQ add-on to start ==="
TIMEOUT=120
ELAPSED=0

# CoppeliaSim v4.7 logs this when the ZMQ add-on script begins running
while ! grep -qE "ZMQ remote API server|zmqRemoteApi" coppeliasim.log 2>/dev/null; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ $ELAPSED -gt $TIMEOUT ]; then
        echo "TIMEOUT: ZMQ add-on never started"
        cat coppeliasim.log
        kill $COPPELIA_PID $XVFB_PID 2>/dev/null || true
        exit 1
    fi
    echo "  waiting for ZMQ log... ${ELAPSED}s"
done

echo "ZMQ add-on detected. Polling TCP port 23000..."

until nc -z localhost 23000 2>/dev/null; do
    sleep 1
    ELAPSED=$((ELAPSED + 1))
    if [ $ELAPSED -gt $TIMEOUT ]; then
        echo "TIMEOUT: port 23000 never became connectable"
        cat coppeliasim.log
        kill $COPPELIA_PID $XVFB_PID 2>/dev/null || true
        exit 1
    fi
    echo "  waiting for port... ${ELAPSED}s"
done

echo "Port 23000 is open. Waiting 3s for scene to finish loading..."
sleep 3

echo "=== Running pytest ==="
export PYTHONPATH=/app
pytest tests/test_regression.py \
    --html=/app/output/report.html \
    --self-contained-html \
    --timeout=90 \
    -vv

TEST_EXIT_CODE=$?
kill -TERM $COPPELIA_PID $XVFB_PID 2>/dev/null || true
exit $TEST_EXIT_CODE