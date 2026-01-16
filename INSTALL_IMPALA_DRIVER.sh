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
# Script to install Impala driver (impyla) in Superset container

set -e

echo "=========================================="
echo "Installing Impala Driver for Superset"
echo "=========================================="
echo ""

CONTAINER_NAME="superset-superset-1"

# Check if container exists
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Error: Container ${CONTAINER_NAME} not found"
    echo "   Make sure Superset is running: docker compose ps"
    exit 1
fi

echo "✅ Found Superset container: ${CONTAINER_NAME}"
echo ""

# Install build dependencies
echo "Installing build dependencies (gcc, python3-dev)..."
docker exec ${CONTAINER_NAME} sh -c "apt-get update -qq && apt-get install -y -qq gcc python3-dev > /dev/null 2>&1"
echo "✅ Build dependencies installed"
echo ""

# Install impyla and dependencies
echo "Installing impyla and thrift-sasl..."
docker exec ${CONTAINER_NAME} pip install --quiet "impyla>0.16.2,<0.17" thrift-sasl
echo "✅ impyla and dependencies installed"
echo ""

# Verify installation
echo "Verifying installation..."
if docker exec ${CONTAINER_NAME} /app/.venv/bin/python -c "import impala.dbapi; print('✅ impyla.dbapi works')" 2>/dev/null; then
    echo "✅ Verification successful"
else
    echo "❌ Verification failed - impyla may not be working correctly"
    exit 1
fi
echo ""

# Restart Superset
echo "Restarting Superset..."
docker compose restart superset
echo "✅ Superset restarted"
echo ""

echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)"
echo "2. Go to Settings → Database Connections → + Database"
echo "3. Look for 'Apache Impala' in the list"
echo "4. Or use SQLAlchemy URI: impala://localhost:21050/default?auth_mechanism=PLAIN"
echo ""
