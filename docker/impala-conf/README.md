# Impala Configuration

This directory contains configuration files for the Impala Docker quickstart setup.

## Files

- `hive-site.xml` - Hive Metastore configuration used by all Impala services

## JDO Dependency Issue

If you see `NoClassDefFoundError: javax.jdo.JDOException` errors in the logs, the services may still be functional for basic operations. The error occurs during metadata initialization but doesn't necessarily prevent query execution.

To fully resolve this, you would need to:
1. Download the JDO API JAR (e.g., `javax.jdo-3.2.1.jar`)
2. Mount it to `/opt/impala/lib` or add it to the classpath
3. Or use a different Impala image that includes all dependencies

For testing purposes, the current setup should work for basic queries even with the JDO warnings.
