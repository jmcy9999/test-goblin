# Test Goblin - Usage Guide

This document provides detailed information on using the Test Goblin command-line tool.

## Table of Contents

- [Command Reference](#command-reference)
- [CLI Options Explained](#cli-options-explained)
- [Example Outputs](#example-outputs)
- [Configuration File Format](#configuration-file-format)
- [Customizing Thresholds](#customizing-thresholds)

## Command Reference

### Main Command

```bash
test-goblin [--version] [--help] <command> [<args>]
```

### Global Options

| Option | Description |
|--------|-------------|
| `--version` | Show program version and exit |
| `--help`, `-h` | Show help message and exit |

### Commands

#### `analyze` - Analyze iOS XCUITest Project

Analyzes an iOS project to extract test inventory, accessibility IDs, test plans, and screen navigation patterns.

```bash
test-goblin analyze <project_path> [OPTIONS]
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `project_path` | Yes | Path to the iOS project root directory |

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--tests-path PATH` | Auto-detect | Custom path to XCUITests directory |
| `--output PATH` | `./analysis/` | Output directory for analysis results |
| `--format FORMATS` | `json,html` | Output formats (comma-separated) |
| `--config PATH` | Auto-detect | Path to configuration file |
| `--verbose` | Off | Enable verbose logging |
| `--quiet` | Off | Suppress progress output |

## CLI Options Explained

### `--tests-path`

By default, the tool auto-detects the XCUITest directory by searching for directories named `*UITests*` or `*XCUITests*`. Use this option to specify a custom location:

```bash
# Project with non-standard test directory
test-goblin analyze /path/to/project --tests-path /path/to/project/MyCustomTests
```

### `--output`

Specifies where to write the analysis results. The directory will be created if it does not exist:

```bash
# Output to custom directory
test-goblin analyze /path/to/project --output ~/Desktop/my-analysis/

# Output to relative path
test-goblin analyze /path/to/project --output ./reports/2024-01/
```

### `--format`

Controls which output formats are generated. Available formats:

- `json` - Machine-readable JSON files for each analyzer
- `html` - Human-readable summary report

```bash
# JSON only (for CI/CD integration)
test-goblin analyze /path/to/project --format json

# Markdown only (for documentation)
test-goblin analyze /path/to/project --format html

# Both formats (default)
test-goblin analyze /path/to/project --format json,html
```

### `--config`

Loads custom thresholds from a JSON configuration file:

```bash
# Use project-specific thresholds
test-goblin analyze /path/to/project --config ./strict-thresholds.json
```

Without this option, the tool searches these locations:
1. `./thresholds.json`
2. `./config/thresholds.json`
3. `~/.test-goblin/thresholds.json`

### `--verbose`

Enables detailed progress logging:

```bash
test-goblin analyze /path/to/project --verbose
```

Output includes:
- Step-by-step progress indicators
- Counts for each analysis phase
- Timing information
- List of generated files

### `--quiet`

Suppresses all progress output (useful for scripting):

```bash
# Silent operation for scripts
test-goblin analyze /path/to/project --quiet && echo "Analysis complete"
```

Note: `--verbose` and `--quiet` are mutually exclusive.

## Example Outputs

### Standard Output (Default)

```
Analyzing iOS project: /Users/dev/MyApp
Output directory: /Users/dev/MyApp/analysis

Generating reports...

Analysis complete!

Results:
  - 57 test files
  - 453 test methods
  - 478 accessibility IDs
  - 9 test plans

Output: /Users/dev/MyApp/analysis
```

### Verbose Output

```
Analyzing iOS project: /Users/dev/MyApp
Output directory: /Users/dev/MyApp/analysis

[1/4] Analyzing test inventory...
  Found 57 test files, 453 test methods
[2/4] Analyzing accessibility IDs...
  Found 478 unique accessibility IDs
[3/4] Analyzing test plans...
  Found 9 test plans
[4/4] Analyzing screen graph...
  Found 73 screens

Generating reports...

Analysis complete!

Results:
  - 57 test files
  - 453 test methods
  - 478 accessibility IDs
  - 9 test plans
  - 73 screens

Output: /Users/dev/MyApp/analysis
Time: 2.34s

Files generated:
  - /Users/dev/MyApp/analysis/test_inventory.json
  - /Users/dev/MyApp/analysis/accessibility_ids.json
  - /Users/dev/MyApp/analysis/test_plans.json
  - /Users/dev/MyApp/analysis/screen_graph.json
  - /Users/dev/MyApp/analysis/ANALYSIS_REPORT.html
```

### JSON Output Format

#### test_inventory.json

```json
{
  "total_test_files": 57,
  "total_test_classes": 62,
  "total_test_methods": 453,
  "naming_convention": {
    "consistency_percentage": 95.4,
    "pattern": "test<Feature><Behavior>"
  },
  "test_files": [
    {
      "file_path": "XCUITests/LoginTests.swift",
      "test_class": "LoginTests",
      "test_methods": ["testLoginSuccess", "testLoginFailure"],
      "test_count": 2
    }
  ]
}
```

#### accessibility_ids.json

```json
{
  "total_unique_ids": 478,
  "centralization_percentage": 67.3,
  "ids_by_usage_count": {
    "high_usage": [
      {"id": "NavigationBar", "count": 156}
    ],
    "medium_usage": [],
    "low_usage": []
  },
  "all_ids": [
    {
      "identifier": "LoginButton",
      "usage_count": 23,
      "source_files": ["LoginTests.swift", "OnboardingTests.swift"]
    }
  ]
}
```

#### test_plans.json

```json
{
  "total_test_plans": 9,
  "test_plans": [
    {
      "name": "SmokeTests",
      "path": "XCUITests/TestPlans/SmokeTests.xctestplan",
      "selection_mode": "selected",
      "included_tests": 45,
      "skipped_tests": 0
    }
  ],
  "coverage_analysis": {
    "tests_in_multiple_plans": 12,
    "orphaned_tests": 5,
    "plan_overlap_percentage": 8.3
  }
}
```

#### screen_graph.json

```json
{
  "screen_graph_detected": true,
  "total_screens": 73,
  "navigator_adoption_percentage": 86.0,
  "screens": [
    {
      "name": "HomeScreen",
      "accessibility_ids": ["HomeTitle", "SettingsButton"],
      "navigation_methods": ["tapSettings", "tapProfile"]
    }
  ]
}
```

### Markdown Report (ANALYSIS_REPORT.html)

The Markdown report includes:

1. **Executive Summary** - Overview of findings
2. **Test Inventory** - File and method counts, naming conventions
3. **Accessibility IDs** - Usage patterns, centralization status
4. **Test Plans** - Coverage analysis, orphaned tests
5. **Screen Graph** - Navigation patterns (if detected)
6. **Recommendations** - Actionable suggestions based on thresholds

## Configuration File Format

The configuration file uses JSON format with the following structure:

```json
{
  "$comment": "Optional comment describing the configuration",

  "test_inventory": {
    "large_file_threshold": 30
  },

  "naming_convention": {
    "consistency_threshold": 90.0
  },

  "accessibility_ids": {
    "generic_id_usage_threshold": 50,
    "centralization_threshold": 50.0
  },

  "test_plans": {
    "orphaned_tests_threshold": 0,
    "multi_plan_tests_threshold": 0,
    "skipped_tests_threshold": 0,
    "overlap_threshold": 10.0
  },

  "screen_graph": {
    "navigator_adoption_threshold": 80.0
  },

  "report": {
    "max_items_in_summary": 20,
    "max_items_before_collapse": 50
  }
}
```

### Configuration Sections

| Section | Description |
|---------|-------------|
| `test_inventory` | Thresholds for test file analysis |
| `naming_convention` | Thresholds for naming pattern analysis |
| `accessibility_ids` | Thresholds for accessibility ID analysis |
| `test_plans` | Thresholds for test plan coverage analysis |
| `screen_graph` | Thresholds for screen navigation analysis |
| `report` | Controls report output formatting |

## Customizing Thresholds

### Test Inventory Thresholds

```json
{
  "test_inventory": {
    "large_file_threshold": 30
  }
}
```

| Threshold | Default | Description |
|-----------|---------|-------------|
| `large_file_threshold` | 30 | Files with more test methods than this trigger "Split Large Files" recommendation |

### Naming Convention Thresholds

```json
{
  "naming_convention": {
    "consistency_threshold": 90.0
  }
}
```

| Threshold | Default | Description |
|-----------|---------|-------------|
| `consistency_threshold` | 90.0 | Below this percentage triggers "Standardize Naming" recommendation |

### Accessibility ID Thresholds

```json
{
  "accessibility_ids": {
    "generic_id_usage_threshold": 50,
    "centralization_threshold": 50.0
  }
}
```

| Threshold | Default | Description |
|-----------|---------|-------------|
| `generic_id_usage_threshold` | 50 | IDs used more than this count trigger "Refine Generic IDs" recommendation |
| `centralization_threshold` | 50.0 | Below this percentage triggers "Centralize IDs" recommendation |

### Test Plan Thresholds

```json
{
  "test_plans": {
    "orphaned_tests_threshold": 0,
    "multi_plan_tests_threshold": 0,
    "skipped_tests_threshold": 0,
    "overlap_threshold": 10.0
  }
}
```

| Threshold | Default | Description |
|-----------|---------|-------------|
| `orphaned_tests_threshold` | 0 | More orphaned tests than this triggers recommendation |
| `multi_plan_tests_threshold` | 0 | Tests in multiple plans above this triggers recommendation |
| `skipped_tests_threshold` | 0 | Skipped tests above this triggers recommendation |
| `overlap_threshold` | 10.0 | Plan overlap below this percentage triggers "Review Coverage" |

### Screen Graph Thresholds

```json
{
  "screen_graph": {
    "navigator_adoption_threshold": 80.0
  }
}
```

| Threshold | Default | Description |
|-----------|---------|-------------|
| `navigator_adoption_threshold` | 80.0 | Below this percentage triggers "Increase Navigator Adoption" recommendation |

### Report Settings

```json
{
  "report": {
    "max_items_in_summary": 20,
    "max_items_before_collapse": 50
  }
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `max_items_in_summary` | 20 | Maximum items shown in summary tables |
| `max_items_before_collapse` | 50 | Show all items if count <= this, otherwise summarize |

### Example: Strict Configuration

For projects with high quality standards:

```json
{
  "$comment": "Strict thresholds for production projects",

  "test_inventory": {
    "large_file_threshold": 20
  },
  "naming_convention": {
    "consistency_threshold": 95.0
  },
  "accessibility_ids": {
    "generic_id_usage_threshold": 30,
    "centralization_threshold": 70.0
  },
  "test_plans": {
    "orphaned_tests_threshold": 0,
    "overlap_threshold": 5.0
  },
  "screen_graph": {
    "navigator_adoption_threshold": 90.0
  }
}
```

### Example: Relaxed Configuration

For legacy projects being gradually improved:

```json
{
  "$comment": "Relaxed thresholds for legacy projects",

  "test_inventory": {
    "large_file_threshold": 50
  },
  "naming_convention": {
    "consistency_threshold": 75.0
  },
  "accessibility_ids": {
    "generic_id_usage_threshold": 100,
    "centralization_threshold": 30.0
  },
  "test_plans": {
    "orphaned_tests_threshold": 10,
    "overlap_threshold": 20.0
  },
  "screen_graph": {
    "navigator_adoption_threshold": 60.0
  }
}
```

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Project path not found |
| 4 | No tests found in project |
| 5 | Analysis failed |

## Troubleshooting

### "No test files found in project"

The tool could not locate XCUITest files. Try:

1. Verify the project path is correct
2. Use `--tests-path` to specify the test directory explicitly
3. Ensure test files follow Swift naming conventions (`*Tests.swift`)

### "Project path not found"

The specified project path does not exist. Verify:

1. The path is spelled correctly
2. You have read permissions for the directory
3. The path uses the correct format for your OS

### Configuration not loading

If custom thresholds are not being applied:

1. Verify the JSON syntax is valid
2. Check file permissions
3. Use `--config` to explicitly specify the path
4. Run with `--verbose` to see configuration loading messages
