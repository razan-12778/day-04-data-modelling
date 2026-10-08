import os
import pytest
from pathlib import Path
from typing import List, Dict, Any
from google.cloud import bigquery
from google.cloud.exceptions import NotFound


class TestImplementationValidation:
    """Test suite for validating BigQuery implementation against expected data quality standards."""

    @pytest.fixture(scope="class")
    def bq_client(self):
        """Initialize BigQuery client using environment variables."""
        project_id = os.getenv("GCP_PROJECT_ID")
        if not project_id:
            pytest.fail("GCP_PROJECT_ID environment variable is not set")

        return bigquery.Client(project=project_id)

    @pytest.fixture(scope="class")
    def project_id(self):
        """Get the GCP project ID from environment."""
        project_id = os.getenv("GCP_PROJECT_ID")
        if not project_id:
            pytest.fail("GCP_PROJECT_ID environment variable is not set")
        return project_id

    @pytest.fixture(scope="class")
    def sql_queries_path(self):
        """Path to SQL validation queries."""
        return Path(__file__).parent / "sql"

    def _load_sql_query(self, sql_file_path: Path, project_id: str) -> str:
        """Load SQL query from file and replace project_id placeholder."""
        if not sql_file_path.exists():
            pytest.fail(f"SQL file not found: {sql_file_path}")

        query = sql_file_path.read_text()
        # Replace any project_id placeholders in the SQL
        query = query.replace("${GCP_PROJECT_ID}", project_id)
        query = query.replace("{project_id}", project_id)

        return query

    def _execute_query(
        self, client: bigquery.Client, query: str
    ) -> List[Dict[str, Any]]:
        """Execute BigQuery query and return results as list of dictionaries."""
        try:
            query_job = client.query(query)
            results = query_job.result()

            # Convert to list of dictionaries for easier testing
            return [dict(row) for row in results]

        except Exception as e:
            pytest.fail(f"Query execution failed: {str(e)}\nQuery: {query}")

    def test_row_count_validation(self, bq_client, project_id, sql_queries_path):
        """Test that row counts match expected values."""
        sql_file = sql_queries_path / "test_row_count.sql"
        query = self._load_sql_query(sql_file, project_id)
        results = self._execute_query(bq_client, query)

        # Expected results based on user specification
        # Allow some flexibility for some items
        expected_counts = {
            "order_items": [112650],
            "raw_sales_transactions": [112650],
            "products": [33022, 32951],
            "customers": [98666],
            "orders": [98666],
        }

        # Convert results to dictionary for easy lookup
        actual_counts = {}
        for row in results:
            table_name = row["table_name"]
            row_count = row["row_count"]
            actual_counts[table_name] = row_count

        # Verify all expected tables are present
        missing_tables = set(expected_counts.keys()) - set(actual_counts.keys())
        if missing_tables:
            pytest.fail(f"Missing tables in results: {missing_tables}")

        # Verify row counts match expectations
        for table_name, expected_count in expected_counts.items():
            actual_count = actual_counts[table_name]
            assert actual_count in expected_count, (
                f"Row count mismatch for {table_name}. "
                f"Expected: {expected_count}, Got: {actual_count}"
            )

        # Verify order_items and raw_sales_transactions have same count
        assert (
            actual_counts["order_items"] == actual_counts["raw_sales_transactions"]
        ), "order_items and raw_sales_transactions should have the same row count"

    def test_referential_integrity_validation(
        self, bq_client, project_id, sql_queries_path
    ):
        """Test that there are no orphaned records (referential integrity violations)."""
        sql_file = sql_queries_path / "test_referential_integrity.sql"
        query = self._load_sql_query(sql_file, project_id)
        results = self._execute_query(bq_client, query)

        # All orphaned record counts should be 0
        for row in results:
            orphaned_count = row.get("orphaned_count", row.get("count", 0))
            validation_type = row.get("validation_type", "unknown")

            assert orphaned_count == 0, (
                f"Found {orphaned_count} orphaned records for {validation_type}. "
                f"All referential integrity checks should return 0."
            )

    def test_data_completeness_validation(
        self, bq_client, project_id, sql_queries_path
    ):
        """Test that key columns don't have NULL values."""
        sql_file = sql_queries_path / "test_data_completeness.sql"
        query = self._load_sql_query(sql_file, project_id)
        results = self._execute_query(bq_client, query)

        # All null counts should be 0 for required fields
        for row in results:
            table_name = row.get("table_name", "unknown")
            null_ids = row.get("null_ids", 0)
            null_names = row.get("null_names", row.get("null_values", 0))

            assert null_ids == 0, (
                f"Found {null_ids} NULL ID values in {table_name}. "
                f"Primary key columns should not contain NULL values."
            )

            # Only check null_names if it exists in the result
            if "null_names" in row or "null_values" in row:
                assert null_names == 0, (
                    f"Found {null_names} NULL name/required values in {table_name}. "
                    f"Required columns should not contain NULL values."
                )

    def test_business_logic_validation(self, bq_client, project_id, sql_queries_path):
        """Test that business logic constraints are maintained."""
        sql_file = sql_queries_path / "test_business_logic.sql"
        query = self._load_sql_query(sql_file, project_id)
        results = self._execute_query(bq_client, query)

        # Should have no mismatched orders
        for row in results:
            mismatched_count = row.get("mismatched_orders", row.get("violations", 0))

            assert mismatched_count == 0, (
                f"Found {mismatched_count} business logic violations. "
                f"Order totals should match when aggregated from order_items."
            )

    def test_tables_schema_data(self, bq_client, project_id):
        """Test that all required normalized tables exist."""
        required_tables = [
            "customers",
            "products",
            "orders",
            "order_items",
            "raw_sales_transactions",
        ]
        dataset_id = "olist_data_modelling"

        for table_name in required_tables:
            table_ref = f"{project_id}.{dataset_id}.{table_name}"

            try:
                table = bq_client.get_table(table_ref)
                assert table is not None, f"Table {table_ref} should exist"

                # Verify table has rows (except possibly raw_sales_transactions)
                if table_name != "raw_sales_transactions":
                    query = f"SELECT COUNT(*) as count FROM `{table_ref}`"
                    result = list(bq_client.query(query).result())[0]
                    row_count = result["count"]

                    assert row_count > 0, f"Table {table_name} should contain data"

            except NotFound:
                pytest.fail(f"Required table {table_ref} does not exist")

        ##### Primary Key Constraints #####
        """Test that tables have primary key constraints defined."""

        # Define expected primary keys for each table
        expected_primary_keys = {
            "customers": ["customer_id"],
            "products": ["product_id"],
            "orders": ["order_id"],
        }

        for table_name, expected_pk_columns in expected_primary_keys.items():
            # Query to check if PRIMARY KEY constraint exists

            pk_constraint_query = f"""
            SELECT
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name,
                kcu.ordinal_position
            FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLE_CONSTRAINTS` tc
            JOIN `{project_id}.{dataset_id}.INFORMATION_SCHEMA.KEY_COLUMN_USAGE` kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_name = kcu.table_name
            WHERE tc.table_name = '{table_name}'
                AND tc.constraint_type = 'PRIMARY KEY'
            ORDER BY kcu.ordinal_position
            """

            results = self._execute_query(bq_client, pk_constraint_query)

            # Check that the primary key constraint exists
            assert len(results) > 0, (
                f"Table {table_name} does not have a PRIMARY KEY constraint defined"
            )

            # Extract actual PK columns from results
            actual_pk_columns = [row["column_name"] for row in results]

            # Verify the PK columns match expressions
            assert actual_pk_columns == expected_pk_columns, (
                f"Primary key mismatch for {table_name}. "
                f"Expected: {expected_pk_columns}, Got: {actual_pk_columns}"
            )

        ##### Schema #####
        """Test that tables have expected column structure."""
        dataset_id = "olist_data_modelling"

        # Expected schema structure (simplified - just checking key columns exist)
        expected_schemas = {
            "customers": ["customer_id", "customer_unique_id", "customer_name"],
            "products": ["product_id", "product_category_name"],
            "orders": ["order_id", "customer_id", "order_status"],
            "order_items": ["order_id", "order_item_id", "product_id", "item_price"],
        }

        for table_name, expected_columns in expected_schemas.items():
            table_ref = f"{project_id}.{dataset_id}.{table_name}"

            try:
                table = bq_client.get_table(table_ref)
                actual_columns = [field.name for field in table.schema]

                for expected_col in expected_columns:
                    assert expected_col in actual_columns, (
                        f"Column {expected_col} missing from table {table_name}. "
                        f"Actual columns: {actual_columns}"
                    )

            except NotFound:
                pytest.fail(f"Table {table_ref} does not exist for schema validation")

        ##### Data Types #####
        """Test that key columns have appropriate data types."""
        dataset_id = "olist_data_modelling"

        # Test monetary columns are NUMERIC (not FLOAT) for precision
        monetary_columns_query = f"""
        SELECT column_name, data_type, table_name
        FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
        WHERE column_name IN ('item_price', 'freight_value')
        AND table_name = 'order_items'
        """

        results = self._execute_query(bq_client, monetary_columns_query)

        for row in results:
            column_name = row["column_name"]
            data_type = row["data_type"]

            assert data_type in ["NUMERIC(10, 2)", "BIGNUMERIC(10, 2)"], (
                f"Monetary column {column_name} should use NUMERIC type, not {data_type}"
            )
