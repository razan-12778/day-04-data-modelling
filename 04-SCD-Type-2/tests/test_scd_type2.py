import os
import pytest
from pathlib import Path
from typing import List, Dict, Any
from google.cloud import bigquery
from google.cloud.exceptions import NotFound


class TestSCDType2Validation:
    """Test suite for validating SCD Type 2 implementation."""

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

    def test_scd_type2_changes_implemented(self, bq_client, project_id, sql_queries_path):
        """Test that SCD Type 2 changes have been implemented (customers with multiple versions exist)."""
        sql_file = sql_queries_path / "test_scd2.sql"
        query = self._load_sql_query(sql_file, project_id)
        results = self._execute_query(bq_client, query)

        # Test should pass if 1 or more customers have multiple versions
        assert len(results) >= 1, (
            f"Expected at least 1 customer with multiple versions (SCD Type 2 changes), "
            f"but found {len(results)}. Make sure you have implemented SCD Type 2 changes "
            f"using the 2-step process (close current record + insert new record)."
        )

        # Verify that the results have the expected structure
        for row in results:
            customer_id = row.get("customer_id")
            versions = row.get("versions")

            assert customer_id is not None, "customer_id should not be None in results"
            assert versions is not None, "versions should not be None in results"
            assert versions > 1, f"Customer {customer_id} should have more than 1 version, got {versions}"

        print(f"✅ SCD Type 2 validation passed: Found {len(results)} customers with multiple versions")

    def test_customers_scd2_table_exists(self, bq_client, project_id):
        """Test that the customers_scd2 table exists and has the expected SCD Type 2 structure."""
        dataset_id = "olist_data_modelling"
        table_name = "customers_scd2"
        table_ref = f"{project_id}.{dataset_id}.{table_name}"

        try:
            table = bq_client.get_table(table_ref)
            assert table is not None, f"Table {table_ref} should exist"

            # Check for required SCD Type 2 columns
            required_scd2_columns = [
                "customer_key",      # Surrogate key
                "customer_id",       # Natural key
                "effective_date",    # When this version became active
                "end_date",         # When this version expired
                "is_current",       # Current flag
                "version_number"    # Version control
            ]

            actual_columns = [field.name for field in table.schema]

            for required_col in required_scd2_columns:
                assert required_col in actual_columns, (
                    f"Required SCD Type 2 column '{required_col}' missing from {table_name}. "
                    f"Actual columns: {actual_columns}"
                )

            # Verify table has data
            query = f"SELECT COUNT(*) as count FROM `{table_ref}`"
            result = list(bq_client.query(query).result())[0]
            row_count = result["count"]

            assert row_count > 0, f"Table {table_name} should contain data"

        except NotFound:
            pytest.fail(f"Required SCD Type 2 table {table_ref} does not exist")

    def test_scd2_data_integrity(self, bq_client, project_id):
        """Test basic SCD Type 2 data integrity rules."""
        dataset_id = "olist_data_modelling"
        table_ref = f"{project_id}.{dataset_id}.customers_scd2"

        # Test 1: Verify no customer has multiple current records
        query = f"""
        SELECT customer_id, COUNT(*) as current_count
        FROM `{table_ref}`
        WHERE is_current = TRUE
        GROUP BY customer_id
        HAVING COUNT(*) > 1
        """

        results = self._execute_query(bq_client, query)
        assert len(results) == 0, (
            f"Found {len(results)} customers with multiple current records. "
            f"Each customer should have exactly one record with is_current = TRUE. "
            f"Violating customers: {[r['customer_id'] for r in results]}"
        )

        # Test 2: Verify current records have NULL end_date
        query = f"""
        SELECT COUNT(*) as invalid_current_records
        FROM `{table_ref}`
        WHERE is_current = TRUE AND end_date IS NOT NULL
        """

        results = self._execute_query(bq_client, query)
        invalid_count = results[0]["invalid_current_records"]

        assert invalid_count == 0, (
            f"Found {invalid_count} current records with non-NULL end_date. "
            f"Records with is_current = TRUE should have end_date = NULL."
        )
