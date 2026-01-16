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
# Simple script to run queries against Impala
# Usage: python3 query_impala.py "SHOW DATABASES"
#        python3 query_impala.py -f query.sql

import sys
import argparse

try:
    from impala.dbapi import connect
    from impala.util import as_pandas
except ImportError:
    print("❌ Error: impyla package not installed.")
    print("   Install it with: pip install 'impyla>0.16.2,<0.17' thrift-sasl")
    print("   Note: The package is named 'impyla' but imports as 'impala'")
    sys.exit(1)


def run_query(query, host="localhost", port=21050, use_pandas=False):
    """Execute a query against Impala and print results."""
    try:
        conn = connect(host=host, port=port, auth_mechanism="NOSASL")
        cursor = conn.cursor()

        # Set memory limit for the query to avoid memory errors
        # Use a very small limit to work within Impala's constrained memory
        try:
            cursor.execute("SET MEM_LIMIT=128m")
            cursor.execute("SET MT_DOP=1")  # Reduce parallelism
        except Exception:
            pass  # Ignore if SET fails, continue with query

        cursor.execute(query)

        # Try to fetch results, but handle DML/DDL statements that don't return results
        try:
            # Check if there are results to fetch
            if cursor.description:
                # Query returns results
                if use_pandas:
                    df = as_pandas(cursor)
                    print(df.to_string())
                else:
                    results = cursor.fetchall()
                    if results:
                        # Print column headers
                        headers = [desc[0] for desc in cursor.description]
                        print(" | ".join(headers))
                        print("-" * (sum(len(str(h)) for h in headers) + len(headers) * 3))
                        # Print rows
                        for row in results:
                            print(" | ".join(str(val) for val in row))
                    else:
                        print("Query executed successfully (no rows returned)")
            else:
                # DDL/DML statement - no results to fetch
                print("Query executed successfully")
        except Exception as fetch_error:
            error_msg = str(fetch_error)
            # Handle the specific Impala error for operations with no results
            if "no results" in error_msg.lower() or "fetch results" in error_msg.lower():
                print("Query executed successfully (no results to return)")
            else:
                # Re-raise if it's a different error
                raise

        cursor.close()
        conn.close()

    except Exception as e:
        error_msg = str(e)
        # Handle the specific Impala error for operations with no results
        if "no results" in error_msg.lower() or "fetch results" in error_msg.lower():
            print("Query executed successfully (no results to return)")
        else:
            print(f"❌ Error: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Run SQL queries against Impala",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 query_impala.py "SHOW DATABASES"
  python3 query_impala.py "SELECT * FROM test_db.rbbn_test LIMIT 10"
  python3 query_impala.py "INSERT INTO test_db.rbbn_test VALUES (1, 'Test', 10.5)"
  python3 query_impala.py -f query.sql
  python3 query_impala.py "SELECT * FROM test_db.rbbn_test" --pandas

Note: Use database.table format for queries, e.g., test_db.rbbn_test
      You cannot combine USE and other statements in one query.
        """,
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="SQL query to execute (or use -f for file)",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Read query from file",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Impala host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=21050,
        help="Impala port (default: 21050)",
    )
    parser.add_argument(
        "--pandas",
        action="store_true",
        help="Output results as pandas DataFrame",
    )

    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            query = f.read()
    elif args.query:
        query = args.query
    else:
        parser.print_help()
        sys.exit(1)

    run_query(query, args.host, args.port, args.pandas)


if __name__ == "__main__":
    main()
