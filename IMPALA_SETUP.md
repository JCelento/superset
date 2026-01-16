# Impala Setup Guide for Superset

Complete guide for setting up Apache Impala locally with Superset.

## Prerequisites

- Docker and Docker Compose installed
- Superset running locally (via `docker compose`)
- At least 4GB RAM allocated to Docker

## Step 1: Start Impala

Start Impala using the provided docker-compose file:

```bash
# If there's an existing version kill that one first
docker compose -f docker-compose-impala.yml down -v

# From the Superset root directory
docker compose -f docker-compose-impala.yml up -d

# Check status (wait 2-3 minutes for full startup)
docker compose -f docker-compose-impala.yml ps
```

Wait until all services show as `healthy`:
- `quickstart-hive-metastore` (HMS)
- `impala-statestored` (StateStore)
- `impala-catalogd` (Catalog)
- `impala-impalad` (Impala Daemon)

**Verify Impala is ready:**
```bash
# Check if port is accessible
nc -z localhost 21050 && echo "✅ Port 21050 is open" || echo "❌ Port not accessible"

# View logs to confirm startup
docker compose -f docker-compose-impala.yml logs impalad | tail -20
```

Look for: `"Impala has started"` in the logs.

## Step 2: Install Impala Driver in Superset

Install the `impyla` driver in your Superset container:

```bash
# Run the installation script
bash INSTALL_IMPALA_DRIVER.sh
```

Or manually:

```bash
# Install build dependencies
docker exec superset-superset-1 sh -c "apt-get update -qq && apt-get install -y -qq gcc python3-dev > /dev/null 2>&1"

# Install impyla and dependencies
docker exec superset-superset-1 pip install --quiet "impyla>0.16.2,<0.17" thrift-sasl

# Restart Superset
docker compose restart superset
```

**Verify installation:**
```bash
docker exec superset-superset-1 pip list | grep -E "(impyla|thrift)"
```

Should show:
- `impyla` (0.16.3)
- `thrift-sasl` (0.4.3)
- `thrift` (0.22.0)
- `thriftpy2` (0.4.20)

## Step 3: Connect Superset to Impala Network

Ensure Superset container can reach Impala:

```bash
# Check if Superset is on the Impala network
docker inspect superset-superset-1 --format '{{range $net, $conf := .NetworkSettings.Networks}}{{$net}} {{end}}' | grep impala-network

# If not connected, connect it:
docker network connect impala-network superset-superset-1
```

## Step 4: Add Impala Database in Superset

1. **Open Superset UI**: `http://localhost:9000`

2. **Navigate to Database Connections**:
   - Click **⚙️ Settings** (gear icon) → **Database Connections** → **+ Database**

3. **Connection Details**:
   - **Display Name**: `Impala Local` (or any name)
   - **SQLAlchemy URI**:
     ```
     impala://impala-impalad:21050/default?auth_mechanism=NOSASL
     ```

   **Important**: Use `auth_mechanism=NOSASL` (not `PLAIN`) to avoid connection timeouts.

4. **Test Connection**:
   - Click **Test Connection** - should show ✅ "Connection looks good!"
   - Click **Connect** to save

### Alternative Connection Strings

**If Superset is running locally (not in Docker):**
```
impala://localhost:21050/default?auth_mechanism=NOSASL
```

**If using host IP:**
```
impala://<YOUR_HOST_IP>:21050/default?auth_mechanism=NOSASL
```

## Step 5: Create Test Data

Once connected, go to **SQL Lab** and run:

```sql
CREATE DATABASE IF NOT EXISTS test_db;
USE test_db;

CREATE TABLE IF NOT EXISTS rbbn_test (
  id INT,
  name STRING,
  value DOUBLE
);

INSERT INTO rbbn_test VALUES
  (1, 'Item 1', 10.5),
  (2, 'Item 2', 20.3),
  (3, 'Item 3', 30.7),
  (4, 'Item 4', 40.1),
  (5, 'Item 5', 50.9);

SELECT * FROM rbbn_test;
```

## Troubleshooting

### Connection Timeout Issues

**Problem**: Connection test takes a long time or times out.

**Solution**: Use `auth_mechanism=NOSASL` instead of `auth_mechanism=PLAIN`:
```
impala://impala-impalad:21050/default?auth_mechanism=NOSASL
```

### Container Not Starting

```bash
# Check logs
docker compose -f docker-compose-impala.yml logs impalad

# Check if ports are in use
netstat -an | grep 21050

# Restart containers
docker compose -f docker-compose-impala.yml restart
```

### Schema Initialization Errors

If you see Derby database errors, clean up volumes:

```bash
docker compose -f docker-compose-impala.yml down -v
docker compose -f docker-compose-impala.yml up -d
```

### Superset Container Issues

```bash
# Check status
docker compose ps superset

# Restart if needed
docker compose restart superset

# Check logs
docker compose logs superset --tail 50
```

### Driver Not Found

```bash
# Verify driver is installed
docker exec superset-superset-1 pip list | grep impyla

# Reinstall if needed
bash INSTALL_IMPALA_DRIVER.sh
```

### Network Connectivity

```bash
# Test from Superset container to Impala
docker exec superset-superset-1 python3 -c "import socket; s = socket.socket(); s.settimeout(2); result = s.connect_ex(('impala-impalad', 21050)); s.close(); print('Port reachable' if result == 0 else 'Port not reachable')"

# Verify containers are on same network
docker network inspect impala-network --format '{{range .Containers}}{{.Name}}{{"\n"}}{{end}}'
```

## Useful Commands

**Check Impala status:**
```bash
docker compose -f docker-compose-impala.yml ps
```

**View Impala logs:**
```bash
docker compose -f docker-compose-impala.yml logs -f impalad
```

**Stop Impala:**
```bash
docker compose -f docker-compose-impala.yml down
```

**Stop and remove data:**
```bash
docker compose -f docker-compose-impala.yml down -v
```

**Restart Impala:**
```bash
docker compose -f docker-compose-impala.yml restart
```

**Restart Superset:**
```bash
docker compose restart superset
```

## Connection Summary

**Working Connection String:**
```
impala://impala-impalad:21050/default?auth_mechanism=NOSASL
```

**Key Points:**
- ✅ Use container name `impala-impalad` (not `localhost`) when Superset is in Docker
- ✅ Use `auth_mechanism=NOSASL` to avoid SASL handshake timeouts
- ✅ Ensure Superset container is on `impala-network`
- ✅ Port `21050` is the HS2 port used by Superset

## Next Steps

After connecting Impala:
1. Create datasets from your tables
2. Build charts and dashboards
3. Test the Impala-specific fixes (e.g., metric labels with spaces)

---

**Last Updated**: Based on working setup with Impala 4.5.0 and Superset
