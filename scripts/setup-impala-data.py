#!/usr/bin/env python3
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
# Script to set up test data in Impala

import sys

try:
    from impyla.dbapi import connect
    from impyla.util import as_pandas
except ImportError:
    print("❌ Error: impyla package not installed.")
    print("   Install it with: pip install impyla")
    sys.exit(1)

def setup_test_data(host="localhost", port=21050):
    """Set up test database and table in Impala."""
    try:
        print(f"Connecting to Impala at {host}:{port}...")
        conn = connect(host=host, port=port, auth_mechanism="PLAIN")
        cursor = conn.cursor()

        print("Creating database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")

        print("Using test_db...")
        cursor.execute("USE test_db")

        print("Creating table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rbbn_test (
              id INT,
              name STRING,
              value DOUBLE
            )
        """)

        print("Checking if table has data...")
        cursor.execute("SELECT COUNT(*) FROM rbbn_test")
        count = cursor.fetchone()[0]

        if count == 0:
            print("Inserting test data...")
            cursor.execute("""
                INSERT INTO rbbn_test VALUES
                  (1, 'Item 1', 10.5),
                  (2, 'Item 2', 20.3),
                  (3, 'Item 3', 30.7),
                  (4, 'Item 4', 40.1),
                  (5, 'Item 5', 50.9)
            """)
            print("✅ Test data inserted")
        else:
            print(f"✅ Table already has {count} rows")

        print("Verifying data...")
        cursor.execute("SELECT COUNT(*) as total FROM rbbn_test")
        result = cursor.fetchone()
        print(f"✅ Total rows: {result[0]}")

        cursor.close()
        conn.close()

        print("\n✅ Setup complete!")
        print("\nConnection details for Superset:")
        print(f"  SQLAlchemy URI: impala://{host}:{port}/test_db?auth_mechanism=PLAIN")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Impala is running: docker compose -f docker-compose-impala.yml ps")
        print("  2. All services are healthy")
        print("  3. Port 21050 is accessible")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Set up test data in Impala")
    parser.add_argument("--host", default="localhost", help="Impala host (default: localhost)")
    parser.add_argument("--port", type=int, default=21050, help="Impala port (default: 21050)")
    args = parser.parse_args()

    setup_test_data(args.host, args.port)
