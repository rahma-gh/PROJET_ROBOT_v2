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

echo "=== Waiting for ZMQ port 23000 to accept connections ==="
TIMEOUT=120
ELAPSED=0

# Step 1: wait for the log line (proves the server started)
while ! grep -q "ZMQ remote API server" coppeliasim.log 2>/dev/null; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ $ELAPSED -gt $TIMEOUT ]; then
        echo "TIMEOUT: CoppeliaSim ZMQ server log never appeared"
        cat coppeliasim.log
        exit 1
    fi
    echo "  waiting for log... ${ELAPSED}s"
done

echo "ZMQ log line detected. Now polling TCP port 23000..."

# Step 2: poll the actual TCP port until it accepts a connection
# nc -z returns 0 as soon as the port is open
until nc -z localhost 23000 2>/dev/null; do
    sleep 1
    ELAPSED=$((ELAPSED + 1))
    if [ $ELAPSED -gt $TIMEOUT ]; then
        echo "TIMEOUT: port 23000 never became connectable"
        cat coppeliasim.log
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
kill -TERM $COPPELIA_PID 2>/dev/null || true
exit $TEST_EXIT_CODE