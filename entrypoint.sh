#!/bin/bash
set -e

echo "=== Initializing environment ==="
export XDG_RUNTIME_DIR=/tmp/runtime-root
mkdir -p "$XDG_RUNTIME_DIR"
chmod 0700 "$XDG_RUNTIME_DIR"

echo "=== Starting CoppeliaSim (headless) ==="

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
    cat coppeliasim.log
    kill -TERM $COPPELIA_PID 2>/dev/null || true
    exit 1
fi

echo "=== coppeliasim.log complet ==="
cat coppeliasim.log
echo "================================"

echo "ZMQ server ready. Waiting for scene to settle..."
sleep 5

echo "=== coppeliasim.log apres sleep ==="
cat coppeliasim.log
echo "===================================="

echo "=== Test connexion ZMQ manuelle ==="
python3 - << 'PYEOF'
import zmq, time
ctx = zmq.Context()
sock = ctx.socket(zmq.REQ)
sock.setsockopt(zmq.RCVTIMEO, 5000)
sock.setsockopt(zmq.SNDTIMEO, 5000)
sock.connect("tcp://localhost:23000")
print("Socket connected")
try:
    import msgpack
    # Envoyer un ping minimal
    msg = msgpack.packb({'func': 'zmqRemoteApi.info', 'args': []})
    sock.send(msg)
    print("Message sent, waiting reply...")
    reply = sock.recv()
    print(f"Reply received: {len(reply)} bytes")
except Exception as e:
    print(f"ERROR: {e}")
finally:
    sock.close()
    ctx.term()
PYEOF

echo "=== Running pytest ==="
export PYTHONPATH=/app

pytest tests/ \
    --html=report.html \
    --self-contained-html \
    --timeout=60 \
    --timeout-method=thread \
    -vv

TEST_EXIT_CODE=$?

echo "=== Stopping CoppeliaSim ==="
kill -TERM $COPPELIA_PID 2>/dev/null || true
timeout 8s wait $COPPELIA_PID 2>/dev/null || true
kill -0 $COPPELIA_PID 2>/dev/null && kill -KILL $COPPELIA_PID 2>/dev/null || true

echo "=== Done (exit code: $TEST_EXIT_CODE) ==="
cat coppeliasim.log
exit $TEST_EXIT_CODE