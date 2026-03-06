#!/bin/bash
set -e

echo "=== Initializing environment ==="
export XDG_RUNTIME_DIR=/tmp/runtime-root
mkdir -p "$XDG_RUNTIME_DIR"
chmod 0700 "$XDG_RUNTIME_DIR"

echo "=== Starting CoppeliaSim (headless) ==="

# SANS -q : ce flag ferme CoppeliaSim immédiatement après le chargement
xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24' \
  /opt/coppelia/coppeliaSim \
    -h \
    -G zmqRemoteApi.rpcPort=23000 \
    -G zmqRemoteApi.cntPort=23001 \
    /app/pick_and_place.ttt > coppeliasim.log 2>&1 &

COPPELIA_PID=$!
echo "CoppeliaSim PID: $COPPELIA_PID"

echo "=== Waiting for ZMQ server ==="
TIMEOUT=300
INTERVAL=2
ELAPSED=0

until grep -q "ZMQ remote API server" coppeliasim.log 2>/dev/null \
   || [ $ELAPSED -ge $TIMEOUT ]; do
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    echo "  waiting... (${ELAPSED}s / ${TIMEOUT}s)"
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "ERROR: ZMQ server not ready after ${TIMEOUT}s"
    tail -n 40 coppeliasim.log
    kill -TERM $COPPELIA_PID 2>/dev/null || true
    exit 1
fi

echo "ZMQ server ready. Waiting for scene to settle..."
sleep 3

echo "=== Running pytest ==="
export PYTHONPATH=/app

pytest tests/ \
    --html=report.html \
    --self-contained-html \
    --timeout=180 \
    --timeout-method=thread \
    -vv

TEST_EXIT_CODE=$?

echo "=== Stopping CoppeliaSim ==="
kill -TERM $COPPELIA_PID 2>/dev/null || true
timeout 8s wait $COPPELIA_PID 2>/dev/null || true
kill -0 $COPPELIA_PID 2>/dev/null && kill -KILL $COPPELIA_PID 2>/dev/null || true

echo "=== Done (exit code: $TEST_EXIT_CODE) ==="
tail -n 20 coppeliasim.log
exit $TEST_EXIT_CODE