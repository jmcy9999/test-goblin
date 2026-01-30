"""Command-line interface for iOS Test Optimizer.

Provides commands for analyzing iOS XCUITest projects and generating reports.
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional

from test_goblin import __version__
from test_goblin.analyzers import (
    AccessibilityAnalyzer,
    ScreenGraphAnalyzer,
)
from test_goblin.analyzers.test_inventory_analyzer import (
    TestInventoryAnalyzer,
)
from test_goblin.analyzers.test_plan_analyzer import TestPlanAnalyzer
from test_goblin.reporters import JSONReporter, HTMLReporter
from test_goblin.reporters.json_reporter import create_metadata
from test_goblin.config import load_config

# Exit codes
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_INVALID_ARGUMENTS = 2
EXIT_PROJECT_NOT_FOUND = 3
EXIT_NO_TESTS_FOUND = 4
EXIT_ANALYSIS_FAILED = 5


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="ios-test-optimizer",
        description="Analyze and optimize iOS XCUITest projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a project with default settings
  ios-test-optimizer analyze /path/to/project

  # Analyze with custom output directory
  ios-test-optimizer analyze /path/to/project --output ./reports/

  # Generate only JSON output
  ios-test-optimizer analyze /path/to/project --format json

  # Verbose mode for detailed progress
  ios-test-optimizer analyze /path/to/project --verbose

For more information, visit: https://github.com/yourusername/ios-test-optimizer
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze iOS XCUITest project and generate reports",
        description="Analyze an iOS XCUITest project to extract test inventory, "
        "accessibility IDs, test plans, and screen navigation patterns.",
    )

    analyze_parser.add_argument(
        "project_path",
        type=str,
        help="Path to the iOS project root directory",
    )

    analyze_parser.add_argument(
        "--tests-path",
        type=str,
        help="Custom path to XCUITests directory (default: auto-detect)",
        default=None,
    )

    analyze_parser.add_argument(
        "--output",
        type=str,
        help="Output directory for analysis results (default: ./analysis/)",
        default="./analysis/",
    )

    analyze_parser.add_argument(
        "--format",
        type=str,
        help="Output formats, comma-separated (default: json,html)",
        default="json,html",
    )

    analyze_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    analyze_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    analyze_parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (default: auto-detect thresholds.json)",
        default=None,
    )

    return parser


def validate_arguments(args: argparse.Namespace) -> Optional[int]:
    """Validate command-line arguments.

    Args:
        args: Parsed arguments

    Returns:
        Exit code if validation fails, None if validation succeeds
    """
    # Validate project path
    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"Error: Project path not found: {args.project_path}", file=sys.stderr)
        return EXIT_PROJECT_NOT_FOUND

    if not project_path.is_dir():
        print(
            f"Error: Project path is not a directory: {args.project_path}",
            file=sys.stderr,
        )
        return EXIT_INVALID_ARGUMENTS

    # Validate output directory
    output_dir = Path(args.output)
    if output_dir.exists() and not output_dir.is_dir():
        print(
            f"Error: Output path exists but is not a directory: {args.output}",
            file=sys.stderr,
        )
        return EXIT_INVALID_ARGUMENTS

    # Validate format
    valid_formats = {"json", "html"}
    requested_formats = {f.strip().lower() for f in args.format.split(",")}
    invalid_formats = requested_formats - valid_formats
    if invalid_formats:
        print(
            f"Error: Invalid format(s): {', '.join(invalid_formats)}. "
            f"Valid formats: {', '.join(valid_formats)}",
            file=sys.stderr,
        )
        return EXIT_INVALID_ARGUMENTS

    # Validate mutually exclusive flags
    if args.verbose and args.quiet:
        print("Error: --verbose and --quiet are mutually exclusive", file=sys.stderr)
        return EXIT_INVALID_ARGUMENTS

    return None


def run_analyze_command(args: argparse.Namespace) -> int:
    """Run the analyze command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code
    """
    # Validate arguments
    validation_result = validate_arguments(args)
    if validation_result is not None:
        return validation_result

    # Load configuration
    config_path = Path(args.config) if args.config else None
    load_config(config_path)

    # Convert paths
    project_path = Path(args.project_path).resolve()
    output_dir = Path(args.output).resolve()

    # Parse output formats
    formats = [f.strip().lower() for f in args.format.split(",")]

    # Start timing
    start_time = time.time()

    if not args.quiet:
        print(f"Analyzing iOS project: {project_path}")
        print(f"Output directory: {output_dir}")
        print()

    # Create output directory
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(
            f"Error: Failed to create output directory: {e}",
            file=sys.stderr,
        )
        return EXIT_GENERAL_ERROR

    # Initialize analyzers
    try:
        if args.verbose:
            print("[1/4] Analyzing test inventory...")

        test_inventory_analyzer = TestInventoryAnalyzer(project_path=project_path)
        test_inventory_results = test_inventory_analyzer.analyze()

        # Check if any tests were found
        if test_inventory_results.get("total_test_methods", 0) == 0:
            print("Error: No test files found in project", file=sys.stderr)
            return EXIT_NO_TESTS_FOUND

        if args.verbose:
            print(
                f"  Found {test_inventory_results['total_test_files']} test files, "
                f"{test_inventory_results['total_test_methods']} test methods"
            )

        if args.verbose:
            print("[2/4] Analyzing accessibility IDs...")

        accessibility_analyzer = AccessibilityAnalyzer(project_path=project_path)
        accessibility_results = accessibility_analyzer.analyze()

        if args.verbose:
            print(
                f"  Found {accessibility_results.get('total_unique_ids', 0)} "
                "unique accessibility IDs"
            )

        if args.verbose:
            print("[3/4] Analyzing test plans...")

        test_plan_analyzer = TestPlanAnalyzer(project_path=project_path)
        test_plan_results = test_plan_analyzer.analyze(
            test_inventory=test_inventory_results
        )

        if args.verbose:
            print(
                f"  Found {len(test_plan_results.get('test_plans', []))} " "test plans"
            )

        if args.verbose:
            print("[4/4] Analyzing screen graph...")

        screen_graph_analyzer = ScreenGraphAnalyzer(project_path=project_path)
        screen_graph_results = screen_graph_analyzer.analyze()

        if args.verbose:
            if screen_graph_results.get("screen_graph_detected", False):
                print(f"  Found {screen_graph_results.get('total_screens', 0)} screens")
            else:
                print("  No screen graph detected (optional)")

    except Exception as e:
        print(f"Error: Analysis failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return EXIT_ANALYSIS_FAILED

    # Generate reports
    try:
        if args.verbose or not args.quiet:
            print()
            print("Generating reports...")

        generated_files: List[str] = []

        # Generate JSON reports
        if "json" in formats:
            json_reporter = JSONReporter(output_dir=output_dir)

            # Create metadata
            metadata = create_metadata(
                project_path=str(project_path),
                tool_version=__version__,
                analyzers_run=[
                    "TestInventoryAnalyzer",
                    "AccessibilityAnalyzer",
                    "TestPlanAnalyzer",
                    "ScreenGraphAnalyzer",
                ],
                execution_time_seconds=time.time() - start_time,
            )

            json_result = json_reporter.generate(
                test_inventory=test_inventory_results,
                accessibility_ids=accessibility_results,
                test_plans=test_plan_results,
                screen_graph=screen_graph_results,
                metadata=metadata,
            )

            if json_result.get("success"):
                # Sort files for consistent ordering
                json_files = sorted(json_result.get("files_written", []))
                generated_files.extend(json_files)
            else:
                print(
                    f"Warning: JSON generation had errors: "
                    f"{json_result.get('errors')}",
                    file=sys.stderr,
                )

        # Generate HTML report
        if "html" in formats:
            html_reporter = HTMLReporter(project_path=project_path)

            report_content = html_reporter.generate_report(
                test_inventory=test_inventory_results,
                accessibility_data=accessibility_results,
                test_plans=test_plan_results,
                screen_graph=screen_graph_results,
            )

            # Write HTML file
            html_file = output_dir / "ANALYSIS_REPORT.html"
            try:
                html_file.write_text(report_content, encoding="utf-8")
                generated_files.append(str(html_file.resolve()))
            except Exception as e:
                print(
                    f"Warning: Failed to write HTML report: {e}",
                    file=sys.stderr,
                )

    except Exception as e:
        print(f"Error: Report generation failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return EXIT_ANALYSIS_FAILED

    # Calculate elapsed time
    elapsed_time = time.time() - start_time

    # Display summary
    if not args.quiet:
        print()
        print("✓ Analysis complete!")
        print()
        print("Results:")
        print(f"  - {test_inventory_results['total_test_files']} test files")
        print(f"  - {test_inventory_results['total_test_methods']} test methods")
        print(
            f"  - {accessibility_results.get('total_unique_ids', 0)} "
            "accessibility IDs"
        )
        print(f"  - {len(test_plan_results.get('test_plans', []))} " "test plans")
        if screen_graph_results.get("screen_graph_detected", False):
            print(f"  - {screen_graph_results.get('total_screens', 0)} screens")
        print()
        print(f"Output: {output_dir}")
        if args.verbose:
            print(f"Time: {elapsed_time:.2f}s")
            print()
            print("Files generated:")
            for file_path in generated_files:
                print(f"  - {file_path}")

    return EXIT_SUCCESS


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args()

    # Route to appropriate command handler
    if args.command == "analyze":
        return run_analyze_command(args)

    # Should never reach here due to required=True in subparsers
    parser.print_help()
    return EXIT_INVALID_ARGUMENTS


if __name__ == "__main__":
    sys.exit(main())
