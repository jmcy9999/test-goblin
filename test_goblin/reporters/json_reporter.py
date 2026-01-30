"""JSON reporter for iOS Test Optimizer.

Generates structured JSON output files from analyzer results with validation
and error handling.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from test_goblin.reporters.base_reporter import BaseReporter


class JSONReporter(BaseReporter):
    """Generates structured JSON outputs from analyzer results.

    Creates the following output files:
    - test_inventory.json - from TestInventoryAnalyzer output
    - accessibility_ids.json - from AccessibilityAnalyzer output
    - test_plans.json - from TestPlanAnalyzer output
    - screen_graph.json - from ScreenGraphAnalyzer output (if available)
    - metadata.json - analysis metadata

    All JSON files are pretty-printed with 2-space indentation and sorted keys.
    """

    def generate(
        self,
        test_inventory: Optional[Dict[str, Any]] = None,
        accessibility_ids: Optional[Dict[str, Any]] = None,
        test_plans: Optional[Dict[str, Any]] = None,
        screen_graph: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate JSON reports from analyzer results.

        Args:
            test_inventory: Test inventory analyzer results
            accessibility_ids: Accessibility analyzer results
            test_plans: Test plan analyzer results
            screen_graph: Screen graph analyzer results (optional)
            metadata: Analysis metadata (timestamp, version, etc.)

        Returns:
            Dictionary with:
                - success: bool - True if all writes succeeded
                - files_written: List[str] - paths of successfully written files
                - errors: List[str] - any errors encountered during generation
        """
        # Ensure output directory exists
        self._ensure_output_dir()

        files_written: List[str] = []
        errors: List[str] = []

        # Write test inventory
        if test_inventory is not None:
            result = self._write_json_file(
                "test_inventory.json", test_inventory, "Test Inventory"
            )
            if result["success"]:
                files_written.append(result["file_path"])
            else:
                errors.extend(result["errors"])

        # Write accessibility IDs
        if accessibility_ids is not None:
            result = self._write_json_file(
                "accessibility_ids.json", accessibility_ids, "Accessibility IDs"
            )
            if result["success"]:
                files_written.append(result["file_path"])
            else:
                errors.extend(result["errors"])

        # Write test plans
        if test_plans is not None:
            result = self._write_json_file("test_plans.json", test_plans, "Test Plans")
            if result["success"]:
                files_written.append(result["file_path"])
            else:
                errors.extend(result["errors"])

        # Write screen graph (always write, even if has_screen_graph is False)
        if screen_graph is not None:
            result = self._write_json_file(
                "screen_graph.json", screen_graph, "Screen Graph"
            )
            if result["success"]:
                files_written.append(result["file_path"])
            else:
                errors.extend(result["errors"])

        # Write metadata
        if metadata is not None:
            # Ensure metadata has ISO 8601 timestamp
            metadata_copy = metadata.copy()
            if "timestamp" not in metadata_copy:
                metadata_copy["timestamp"] = datetime.now(timezone.utc).isoformat()

            result = self._write_json_file("metadata.json", metadata_copy, "Metadata")
            if result["success"]:
                files_written.append(result["file_path"])
            else:
                errors.extend(result["errors"])

        # Return summary
        return {
            "success": len(errors) == 0,
            "files_written": files_written,
            "errors": errors,
        }

    def _write_json_file(
        self, filename: str, data: Dict[str, Any], description: str
    ) -> Dict[str, Any]:
        """Write a JSON file with error handling and validation.

        Args:
            filename: Name of the file to write
            data: Data to serialize to JSON
            description: Human-readable description for error messages

        Returns:
            Dictionary with:
                - success: bool
                - file_path: str (absolute path if successful)
                - errors: List[str]
        """
        file_path = self.output_dir / filename
        errors: List[str] = []

        try:
            # Validate that data is JSON-serializable
            json_str = json.dumps(data, indent=2, sort_keys=True)

            # Write to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_str)

            return {
                "success": True,
                "file_path": str(file_path.absolute()),
                "errors": [],
            }

        except TypeError as e:
            error_msg = f"Failed to serialize {description} to JSON: {e}"
            errors.append(error_msg)

        except IOError as e:
            error_msg = f"Failed to write {description} to {file_path}: {e}"
            errors.append(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error writing {description}: {e}"
            errors.append(error_msg)

        return {
            "success": False,
            "file_path": "",
            "errors": errors,
        }


def create_metadata(
    project_path: str,
    tool_version: str = "1.0.0",
    analyzers_run: Optional[List[str]] = None,
    execution_time_seconds: float = 0.0,
) -> Dict[str, Any]:
    """Create metadata dictionary for JSON reporter.

    Args:
        project_path: Path to the analyzed project
        tool_version: Version of the tool (default: "1.0.0")
        analyzers_run: List of analyzer names that were executed
        execution_time_seconds: Total execution time in seconds

    Returns:
        Metadata dictionary with ISO 8601 timestamp
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_path": project_path,
        "tool_version": tool_version,
        "analyzers_run": analyzers_run or [],
        "execution_time_seconds": execution_time_seconds,
    }
