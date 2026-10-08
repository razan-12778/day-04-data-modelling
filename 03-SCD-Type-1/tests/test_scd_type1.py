import os
import pytest
from pathlib import Path
from typing import List, Dict, Any
from google.cloud import bigquery
from google.cloud.exceptions import NotFound


class TestSCDType1Validation:
    """Test suite for validating SCD Type 1 audit field implementation."""

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

    def test_audit_fields_populated(self, bq_client, project_id, sql_queries_path):
        """Test that all tables have audit fields properly populated."""
        sql_file = sql_queries_path / "verify_updated_schema.sql"
        query = self._load_sql_query(sql_file, project_id)
        results = self._execute_query(bq_client, query)

        # Expected results based on user specification
        expected_results = {
            "customers": {
                "total_records": 98666,
                "populated_created": 98666,
                "populated_updated": 98666,
                "populated_version": 98666,
            },
            "products": {
                "total_records": 33022,
                "populated_created": 33022,
                "populated_updated": 33022,
                "populated_version": 33022,
            },
            "orders": {
                "total_records": 98666,
                "populated_created": 98666,
                "populated_updated": 98666,
                "populated_version": 98666,
            },
            "order_items": {
                "total_records": 112650,
                "populated_created": 112650,
                "populated_updated": 112650,
                "populated_version": 112650,
            },
        }

        # Convert results to dictionary for easy lookup
        actual_results = {}
        for row in results:
            table_name = row["table_name"]
            actual_results[table_name] = {
                "total_records": row["total_records"],
                "populated_created": row["populated_created"],
                "populated_updated": row["populated_updated"],
                "populated_version": row["populated_version"],
            }

        # Verify all expected tables are present
        missing_tables = set(expected_results.keys()) - set(actual_results.keys())
        if missing_tables:
            pytest.fail(f"Missing tables in results: {missing_tables}")

        # Verify audit field population for each table
        for table_name, expected in expected_results.items():
            actual = actual_results[table_name]

            # Check total record count matches expected
            assert actual["total_records"] == expected["total_records"], (
                f"Total record count mismatch for {table_name}. "
                f"Expected: {expected['total_records']}, Got: {actual['total_records']}"
            )

            # Check that all audit fields are fully populated (no NULLs)
            assert actual["populated_created"] == expected["populated_created"], (
                f"record_created_date not fully populated for {table_name}. "
                f"Expected: {expected['populated_created']}, Got: {actual['populated_created']}"
            )

            assert actual["populated_updated"] == expected["populated_updated"], (
                f"record_last_updated not fully populated for {table_name}. "
                f"Expected: {expected['populated_updated']}, Got: {actual['populated_updated']}"
            )

            assert actual["populated_version"] == expected["populated_version"], (
                f"data_version not fully populated for {table_name}. "
                f"Expected: {expected['populated_version']}, Got: {actual['populated_version']}"
            )

            # Verify that populated counts match total record counts (no NULLs)
            assert actual["total_records"] == actual["populated_created"], (
                f"record_created_date has NULL values for {table_name}. "
                f"Total records: {actual['total_records']}, Populated: {actual['populated_created']}"
            )

            assert actual["total_records"] == actual["populated_updated"], (
                f"record_last_updated has NULL values for {table_name}. "
                f"Total records: {actual['total_records']}, Populated: {actual['populated_updated']}"
            )

            assert actual["total_records"] == actual["populated_version"], (
                f"data_version has NULL values for {table_name}. "
                f"Total records: {actual['total_records']}, Populated: {actual['populated_version']}"
            )

    def test_tables_have_audit_columns(self, bq_client, project_id):
        """Test that all required tables have the audit columns in their schema."""
        required_tables = ["customers", "products", "orders", "order_items"]
        required_audit_columns = [
            "record_created_date",
            "record_last_updated",
            "data_version",
        ]
        dataset_id = "olist_data_modelling"

        for table_name in required_tables:
            table_ref = f"{project_id}.{dataset_id}.{table_name}"

            try:
                table = bq_client.get_table(table_ref)
                actual_columns = [field.name for field in table.schema]

                for audit_col in required_audit_columns:
                    assert audit_col in actual_columns, (
                        f"Audit column {audit_col} missing from table {table_name}. "
                        f"Make sure you have run the ALTER TABLE statements to add audit fields."
                    )

            except NotFound:
                pytest.fail(f"Required table {table_ref} does not exist")

    def test_audit_column_data_types(self, bq_client, project_id):
        """Test that audit columns have correct data types."""
        dataset_id = "olist_data_modelling"
        required_tables = ["customers", "products", "orders", "order_items"]

        expected_types = {
            "record_created_date": "TIMESTAMP",
            "record_last_updated": "TIMESTAMP",
            "data_version": "INTEGER",
        }

        for table_name in required_tables:
            table_ref = f"{project_id}.{dataset_id}.{table_name}"

            try:
                table = bq_client.get_table(table_ref)

                for field in table.schema:
                    if field.name in expected_types:
                        expected_type = expected_types[field.name]
                        actual_type = field.field_type

                        assert actual_type == expected_type, (
                            f"Incorrect data type for {field.name} in {table_name}. "
                            f"Expected: {expected_type}, Got: {actual_type}"
                        )

            except NotFound:
                pytest.fail(f"Required table {table_ref} does not exist")
