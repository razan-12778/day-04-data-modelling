import pytest
from pydbml import PyDBML
from pathlib import Path
from typing import Dict, Tuple, Set


class TestSchemaValidation:
    """Test suite for validating DBML schema against target schema."""

    @pytest.fixture(scope="class")
    def schema_parsed(self):
        """Load and parse the schema.dbml file."""
        project_root = Path(__file__).parent.parent
        schema_path = project_root / "dbml" / "schema.dbml"

        if not schema_path.exists():
            pytest.fail(f"Schema file not found at: {schema_path}")

        return PyDBML(schema_path)

    @pytest.fixture(scope="class")
    def target_schema_parsed(self):
        """Load and parse the target_schema.dbml file."""
        project_root = Path(__file__).parent.parent
        target_path = project_root / "tests" / "data" / "target_schema.dbml"

        if not target_path.exists():
            pytest.fail(f"Target schema file not found at: {target_path}")

        return PyDBML(target_path)

    def _normalize_data_type(self, data_type: str) -> str:
        """Normalize data types for comparison (case-insensitive)."""
        return data_type.upper().strip()

    def _extract_table_info(self, parsed_schema, table_name: str) -> Dict:
        """Extract table information including columns, types, and primary keys."""
        # Check if table exists and provide helpful error message
        available_tables = [table.name for table in parsed_schema.tables]

        if table_name not in available_tables:
            pytest.fail(
                f"Table '{table_name}' not found in schema. "
                f"Available tables: {available_tables}. "
                f"Make sure your schema.dbml file contains the table definition for '{table_name}'."
            )

        table = parsed_schema[f"public.{table_name}"]

        columns = {}
        primary_keys = []

        for column in table.columns:
            columns[column.name] = self._normalize_data_type(column.type)
            if column.pk:
                primary_keys.append(column.name)

        return {"columns": columns, "primary_keys": primary_keys}

    def test_customers_table(self, schema_parsed, target_schema_parsed):
        """Test customers table structure."""
        schema_info = self._extract_table_info(schema_parsed, "customers")
        target_info = self._extract_table_info(target_schema_parsed, "customers")

        # Check column names
        assert set(schema_info["columns"].keys()) == set(
            target_info["columns"].keys()
        ), (
            f"Column names mismatch. Expected: {set(target_info['columns'].keys())}, Got: {set(schema_info['columns'].keys())}"
        )

        # Check data types
        for col_name in schema_info["columns"]:
            assert (
                schema_info["columns"][col_name] == target_info["columns"][col_name]
            ), (
                f"Data type mismatch for column '{col_name}'. Expected: {target_info['columns'][col_name]}, Got: {schema_info['columns'][col_name]}"
            )

        # Check primary keys
        assert set(schema_info["primary_keys"]) == set(target_info["primary_keys"]), (
            f"Primary key mismatch. Expected: {set(target_info['primary_keys'])}, Got: {set(schema_info['primary_keys'])}"
        )

    def test_products_table(self, schema_parsed, target_schema_parsed):
        """Test products table structure."""
        schema_info = self._extract_table_info(schema_parsed, "products")
        target_info = self._extract_table_info(target_schema_parsed, "products")

        # Check column names
        assert set(schema_info["columns"].keys()) == set(
            target_info["columns"].keys()
        ), (
            f"Column names mismatch. Expected: {set(target_info['columns'].keys())}, Got: {set(schema_info['columns'].keys())}"
        )

        # Check data types
        for col_name in schema_info["columns"]:
            assert (
                schema_info["columns"][col_name] == target_info["columns"][col_name]
            ), (
                f"Data type mismatch for column '{col_name}'. Expected: {target_info['columns'][col_name]}, Got: {schema_info['columns'][col_name]}"
            )

        # Check primary keys
        assert set(schema_info["primary_keys"]) == set(target_info["primary_keys"]), (
            f"Primary key mismatch. Expected: {set(target_info['primary_keys'])}, Got: {set(schema_info['primary_keys'])}"
        )

    def test_orders_table(self, schema_parsed, target_schema_parsed):
        """Test orders table structure."""
        schema_info = self._extract_table_info(schema_parsed, "orders")
        target_info = self._extract_table_info(target_schema_parsed, "orders")

        # Check column names
        assert set(schema_info["columns"].keys()) == set(
            target_info["columns"].keys()
        ), (
            f"Column names mismatch. Expected: {set(target_info['columns'].keys())}, Got: {set(schema_info['columns'].keys())}"
        )

        # Check data types
        for col_name in schema_info["columns"]:
            assert (
                schema_info["columns"][col_name] == target_info["columns"][col_name]
            ), (
                f"Data type mismatch for column '{col_name}'. Expected: {target_info['columns'][col_name]}, Got: {schema_info['columns'][col_name]}"
            )

        # Check primary keys
        assert set(schema_info["primary_keys"]) == set(target_info["primary_keys"]), (
            f"Primary key mismatch. Expected: {set(target_info['primary_keys'])}, Got: {set(schema_info['primary_keys'])}"
        )

    def test_order_items_table(self, schema_parsed, target_schema_parsed):
        """Test order_items table structure."""
        schema_info = self._extract_table_info(schema_parsed, "order_items")
        target_info = self._extract_table_info(target_schema_parsed, "order_items")

        # Check column names
        assert set(schema_info["columns"].keys()) == set(
            target_info["columns"].keys()
        ), (
            f"Column names mismatch. Expected: {set(target_info['columns'].keys())}, Got: {set(schema_info['columns'].keys())}"
        )

        # Check data types
        for col_name in schema_info["columns"]:
            assert (
                schema_info["columns"][col_name] == target_info["columns"][col_name]
            ), (
                f"Data type mismatch for column '{col_name}'. Expected: {target_info['columns'][col_name]}, Got: {schema_info['columns'][col_name]}"
            )

        # Check primary keys
        assert set(schema_info["primary_keys"]) == set(target_info["primary_keys"]), (
            f"Primary key mismatch. Expected: {set(target_info['primary_keys'])}, Got: {set(schema_info['primary_keys'])}"
        )

    def _extract_references(self, parsed_schema) -> Set[Tuple[str, str]]:
        """Extract references as normalized tuples for flexible comparison."""
        references = set()

        # Handle directionality in references
        for ref in parsed_schema.refs:
            if ref.type == "<":
                left = ref.table1.name + "." + ref.col1[0].name
                right = ref.table2.name + "." + ref.col2[0].name
            elif ref.type == ">":
                left = ref.table2.name + "." + ref.col2[0].name
                right = ref.table1.name + "." + ref.col1[0].name
            else:
                pytest.fail(
                    f"Incorrect reference type between tables: {ref.table1.name} and {ref.table2.name}"
                )

            references.add(tuple([left, right]))

        return references

    def test_references(self, schema_parsed, target_schema_parsed):
        """Test that all required references exist (flexible about direction)."""
        schema_refs = self._extract_references(schema_parsed)
        target_refs = self._extract_references(target_schema_parsed)

        # Check that all target references exist in schema (regardless of direction)
        missing_refs = target_refs - schema_refs
        extra_refs = schema_refs - target_refs

        assert len(missing_refs) == 0, f"Missing references: {missing_refs}"

        assert len(extra_refs) == 0, f"Extra references found: {extra_refs}"

        assert schema_refs == target_refs, (
            f"Reference mismatch. Expected: {target_refs}, Got: {schema_refs}"
        )
