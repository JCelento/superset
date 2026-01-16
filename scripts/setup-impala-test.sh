#!/bin/bash
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and
# limitations under the License.
#
# Helper script to set up Impala for testing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Impala Test Setup Script"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if docker-compose-impala.yml exists
if [ ! -f "$PROJECT_ROOT/docker-compose-impala.yml" ]; then
    echo "❌ Error: docker-compose-impala.yml not found in project root"
    exit 1
fi

echo "Starting Impala container..."
cd "$PROJECT_ROOT"
docker compose -f docker-compose-impala.yml up -d

echo ""
echo "Waiting for Impala to be ready (this may take 2-3 minutes)..."
echo ""

# Wait for Impala services to be ready
echo "Waiting for Impala services to start..."
echo "  - Hive Metastore (HMS)"
echo "  - StateStore"
echo "  - Catalog"
echo "  - Impala Daemon"
echo ""

MAX_ATTEMPTS=120
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    # Check if impalad process is running and port is accessible
    if docker exec impala-impalad pgrep -f impalad > /dev/null 2>&1 && \
       timeout 2 bash -c "cat < /dev/null > /dev/tcp/localhost/21050" 2>/dev/null; then
        echo "✅ Impala is ready!"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    if [ $((ATTEMPT % 15)) -eq 0 ]; then
        echo "   Still waiting... (${ATTEMPT}/${MAX_ATTEMPTS})"
        echo "   Check service status:"
        docker compose -f docker-compose-impala.yml ps --format "table {{.Name}}\t{{.Status}}"
    fi
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo ""
    echo "⚠️  Warning: Impala may not be fully ready yet."
    echo ""
    echo "Check service status:"
    docker compose -f docker-compose-impala.yml ps
    echo ""
    echo "Check logs:"
    echo "   docker compose -f docker-compose-impala.yml logs impalad"
    echo ""
    echo "Note: Impala can take 3-5 minutes to fully start."
    echo "You can manually test the connection from Superset UI."
    exit 1
fi

echo ""
echo "Setting up test database and table..."
echo ""

# Try using Python script with impyla
if command -v python3 > /dev/null 2>&1 && python3 -c "import impyla" 2>/dev/null; then
    echo "Using Python impyla client to set up test data..."
    python3 "$SCRIPT_DIR/setup-impala-data.py"
elif command -v python > /dev/null 2>&1 && python -c "import impyla" 2>/dev/null; then
    echo "Using Python impyla client to set up test data..."
    python "$SCRIPT_DIR/setup-impala-data.py"
else
    echo "⚠️  impyla Python package not found."
    echo "   Install it with: pip install impyla"
    echo ""
    echo "   Or create the test database manually from Superset UI:"
    echo "   SQL to run:"
    echo "   CREATE DATABASE IF NOT EXISTS test_db;"
    echo "   USE test_db;"
    echo "   CREATE TABLE IF NOT EXISTS rbbn_test (id INT, name STRING, value DOUBLE);"
    echo "   INSERT INTO rbbn_test VALUES (1, 'Item 1', 10.5), (2, 'Item 2', 20.3),"
    echo "     (3, 'Item 3', 30.7), (4, 'Item 4', 40.1), (5, 'Item 5', 50.9);"
fi

echo ""
echo "=========================================="
echo "✅ Impala setup complete!"
echo "=========================================="
echo ""
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 21050"
echo "  Database: test_db"
echo "  Table: rbbn_test"
echo ""
echo "SQLAlchemy URI for Superset:"
echo "  impala://localhost:21050/test_db?auth_mechanism=PLAIN"
echo ""
echo "To view logs:"
echo "  docker compose -f docker-compose-impala.yml logs -f impala"
echo ""
echo "To stop Impala:"
echo "  docker compose -f docker-compose-impala.yml down"
echo ""
