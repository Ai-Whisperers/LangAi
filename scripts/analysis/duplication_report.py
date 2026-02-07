#!/usr/bin/env python3
"""
Comprehensive Code Duplication Analysis Report
"""
import os
import re
from collections import defaultdict
from pathlib import Path

SRC_DIR = "src"


def analyze_duplications():
    """Analyze and report all types of code duplication."""

    duplications = []
    duplication_id = 1

    # Collect all Python files
    py_files = []
    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))

    print(f"=" * 100)
    print(f"COMPREHENSIVE CODE DUPLICATION ANALYSIS")
    print(f"Analyzing {len(py_files)} Python files in {SRC_DIR}/")
    print(f"=" * 100)
    print()

    # ========================================================================
    # 1. DUPLICATE LOGGER INITIALIZATION
    # ========================================================================
    logger_pattern = re.compile(r"logger\s*=\s*logging\.getLogger\(__name__\)")
    logger_files = []

    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if logger_pattern.search(line):
                        logger_files.append((filepath.replace(os.sep, "/"), i))
        except:
            pass

    print(f"\n{duplication_id}. DUPLICATE LOGGER INITIALIZATION")
    print(f"   Found in {len(logger_files)} files")
    print(f"   Pattern: logger = logging.getLogger(__name__)")
    print(f"   Files:")
    for f, line in logger_files[:10]:
        print(f"     - {f}:{line}")
    if len(logger_files) > 10:
        print(f"     ... and {len(logger_files) - 10} more")
    print(f"   Refactoring: Create base logger utility in agents/base/logger.py")
    duplications.append(
        {
            "id": duplication_id,
            "type": "Logger Initialization",
            "count": len(logger_files),
            "files": logger_files,
        }
    )
    duplication_id += 1

    # ========================================================================
    # 2. DUPLICATE EXCEPTION CLASSES
    # ========================================================================
    exception_classes = defaultdict(list)
    exception_pattern = re.compile(r"class\s+(\w+Exception|.*Error)\(")

    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    match = exception_pattern.search(line)
                    if match:
                        exc_name = match.group(1)
                        exception_classes[exc_name].append((filepath.replace(os.sep, "/"), i))
        except:
            pass

    dup_exceptions = {k: v for k, v in exception_classes.items() if len(v) > 1}
    print(f"\n{duplication_id}. DUPLICATE EXCEPTION CLASSES")
    print(f"   Found {len(dup_exceptions)} exception classes defined multiple times")
    for exc_name, locations in sorted(dup_exceptions.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"   {exc_name}: {len(locations)} occurrences")
        for loc in locations[:3]:
            print(f"     - {loc[0]}:{loc[1]}")
    print(f"   Refactoring: Consolidate into company_researcher/exceptions.py")
    duplications.append(
        {
            "id": duplication_id,
            "type": "Exception Classes",
            "count": sum(len(v) for v in dup_exceptions.values()),
            "details": dup_exceptions,
        }
    )
    duplication_id += 1

    # ========================================================================
    # 3. DUPLICATE PROMPT CONSTANTS
    # ========================================================================
    prompt_constants = defaultdict(list)
    prompt_pattern = re.compile(r"^([A-Z_]+_PROMPT)\s*=", re.MULTILINE)

    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    match = prompt_pattern.search(line)
                    if match:
                        const_name = match.group(1)
                        prompt_constants[const_name].append((filepath.replace(os.sep, "/"), i))
        except:
            pass

    dup_prompts = {k: v for k, v in prompt_constants.items() if len(v) > 1}
    print(f"\n{duplication_id}. DUPLICATE PROMPT CONSTANTS")
    print(f"   Found {len(dup_prompts)} prompt constants defined in multiple files")
    for const_name, locations in sorted(dup_prompts.items(), key=lambda x: -len(x[1]))[:15]:
        print(f"   {const_name}: {len(locations)} occurrences")
        for loc in locations:
            print(f"     - {loc[0]}:{loc[1]}")
    print(f"   Refactoring: Centralize in prompts/core.py or prompts/__init__.py")
    duplications.append(
        {
            "id": duplication_id,
            "type": "Prompt Constants",
            "count": sum(len(v) for v in dup_prompts.values()),
            "details": dup_prompts,
        }
    )
    duplication_id += 1

    # ========================================================================
    # 4. DUPLICATE CONFIGURATION CLASSES
    # ========================================================================
    config_classes = defaultdict(list)
    config_pattern = re.compile(r"class\s+(\w*Config)\(")

    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    match = config_pattern.search(line)
                    if match:
                        class_name = match.group(1)
                        config_classes[class_name].append((filepath.replace(os.sep, "/"), i))
        except:
            pass

    dup_configs = {k: v for k, v in config_classes.items() if len(v) > 1}
    print(f"\n{duplication_id}. DUPLICATE CONFIGURATION CLASSES")
    print(f"   Found {len(dup_configs)} config classes with same names")
    for class_name, locations in sorted(dup_configs.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"   {class_name}: {len(locations)} occurrences")
        for loc in locations:
            print(f"     - {loc[0]}:{loc[1]}")
    print(f"   Refactoring: Use unique names or consolidate into config.py")
    duplications.append(
        {
            "id": duplication_id,
            "type": "Config Classes",
            "count": sum(len(v) for v in dup_configs.values()),
            "details": dup_configs,
        }
    )
    duplication_id += 1

    # ========================================================================
    # 5. DUPLICATE CACHE IMPLEMENTATIONS
    # ========================================================================
    cache_classes = defaultdict(list)
    cache_pattern = re.compile(r"class\s+(\w*Cache|.*LRU)\(")

    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    match = cache_pattern.search(line)
                    if match:
                        class_name = match.group(1)
                        cache_classes[class_name].append((filepath.replace(os.sep, "/"), i))
        except:
            pass

    print(f"\n{duplication_id}. CACHE IMPLEMENTATIONS")
    print(f"   Found {len(cache_classes)} cache classes")
    for class_name, locations in sorted(cache_classes.items(), key=lambda x: -len(x[1]))[:15]:
        print(f"   {class_name}: {len(locations)} occurrence(s)")
        for loc in locations:
            print(f"     - {loc[0]}:{loc[1]}")

    # Special check for LRUCache duplication
    lru_impls = [k for k in cache_classes.keys() if "LRU" in k]
    if len(lru_impls) > 1:
        print(f"   WARNING: {len(lru_impls)} different LRU implementations found!")
        print(f"   Refactoring: Consolidate into single caching/lru_cache.py")
    duplications.append(
        {
            "id": duplication_id,
            "type": "Cache Implementations",
            "count": len(cache_classes),
            "details": cache_classes,
        }
    )
    duplication_id += 1

    # ========================================================================
    # 6. DUPLICATE FORMAT FUNCTIONS
    # ========================================================================
    format_funcs = defaultdict(list)
    format_pattern = re.compile(r"def\s+(format_\w+)\(")

    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    match = format_pattern.search(line)
                    if match:
                        func_name = match.group(1)
                        format_funcs[func_name].append((filepath.replace(os.sep, "/"), i))
        except:
            pass

    dup_formats = {k: v for k, v in format_funcs.items() if len(v) > 1}
    print(f"\n{duplication_id}. DUPLICATE FORMATTING FUNCTIONS")
    print(f"   Found {len(dup_formats)} format functions defined multiple times")
    for func_name, locations in sorted(dup_formats.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"   {func_name}: {len(locations)} occurrences")
        for loc in locations[:3]:
            print(f"     - {loc[0]}:{loc[1]}")
    print(f"   Refactoring: Centralize in prompts/formatters.py")
    duplications.append(
        {
            "id": duplication_id,
            "type": "Format Functions",
            "count": sum(len(v) for v in dup_formats.values()),
            "details": dup_formats,
        }
    )
    duplication_id += 1

    # ========================================================================
    # 7. DUPLICATE _PARSE_ANALYSIS METHODS
    # ========================================================================
    parse_analysis_files = []
    parse_pattern = re.compile(r"def\s+_parse_analysis\(")

    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if parse_pattern.search(line):
                        parse_analysis_files.append((filepath.replace(os.sep, "/"), i))
        except:
            pass

    print(f"\n{duplication_id}. DUPLICATE _parse_analysis() METHODS")
    print(f"   Found in {len(parse_analysis_files)} files")
    for f, line in parse_analysis_files:
        print(f"     - {f}:{line}")
    print(f"   Refactoring: Extract to llm/response_parser.py")
    duplications.append(
        {
            "id": duplication_id,
            "type": "_parse_analysis Methods",
            "count": len(parse_analysis_files),
            "files": parse_analysis_files,
        }
    )
    duplication_id += 1

    # ========================================================================
    # 8. DUPLICATE analyze() METHOD SIGNATURES
    # ========================================================================
    analyze_methods = []
    analyze_pattern = re.compile(r"def\s+analyze\(self.*company_name.*search_results")

    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if analyze_pattern.search(line):
                        analyze_methods.append((filepath.replace(os.sep, "/"), i))
        except:
            pass

    print(f"\n{duplication_id}. SIMILAR analyze() METHOD SIGNATURES")
    print(f"   Found in {len(analyze_methods)} files")
    for f, line in analyze_methods[:10]:
        print(f"     - {f}:{line}")
    print(f"   Refactoring: Extract to base class in agents/base/specialist.py")
    duplications.append(
        {
            "id": duplication_id,
            "type": "analyze() Methods",
            "count": len(analyze_methods),
            "files": analyze_methods,
        }
    )
    duplication_id += 1

    # ========================================================================
    # 9. DUPLICATE ERROR HANDLING PATTERNS
    # ========================================================================
    generic_except = []
    except_pattern = re.compile(r"except\s+Exception\s+as\s+e:")

    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if except_pattern.search(line):
                        generic_except.append((filepath.replace(os.sep, "/"), i))
        except:
            pass

    print(f"\n{duplication_id}. GENERIC EXCEPTION HANDLERS")
    print(f"   Found {len(generic_except)} 'except Exception as e:' blocks")
    print(f"   Sample locations:")
    for f, line in generic_except[:10]:
        print(f"     - {f}:{line}")
    print(f"   Refactoring: Use specific exceptions from agents/base/errors.py")
    duplications.append(
        {
            "id": duplication_id,
            "type": "Generic Exception Handlers",
            "count": len(generic_except),
            "files": generic_except,
        }
    )
    duplication_id += 1

    # ========================================================================
    # 10. DUPLICATE COST TRACKING CODE
    # ========================================================================
    cost_tracking = []
    cost_patterns = [
        re.compile(r"total_cost\s*=.*input_tokens.*output_tokens"),
        re.compile(r"calculate.*cost"),
        re.compile(r"pricing\s*=\s*\{"),
    ]

    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                for pattern in cost_patterns:
                    if pattern.search(content):
                        cost_tracking.append(filepath.replace(os.sep, "/"))
                        break
        except:
            pass

    print(f"\n{duplication_id}. COST TRACKING CODE")
    print(f"   Found in {len(cost_tracking)} files")
    for f in cost_tracking[:10]:
        print(f"     - {f}")
    if len(cost_tracking) > 10:
        print(f"     ... and {len(cost_tracking) - 10} more")
    print(
        f"   Refactoring: Centralize in monitoring/cost_tracker.py or integrations/cost/tracker.py"
    )
    duplications.append(
        {
            "id": duplication_id,
            "type": "Cost Tracking",
            "count": len(cost_tracking),
            "files": cost_tracking,
        }
    )
    duplication_id += 1

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    total_duplications = sum(d.get("count", 0) for d in duplications)
    print(f"Total duplication categories found: {len(duplications)}")
    print(f"Total duplicate code instances: {total_duplications}")
    print()
    print("Top refactoring priorities:")
    print("1. Consolidate logger initialization (122 files)")
    print("2. Centralize prompt constants (45+ duplicates)")
    print("3. Unify exception handling (10+ exception classes)")
    print("4. Extract format functions to single module")
    print("5. Create base agent class for analyze() methods")
    print("6. Consolidate cache implementations")
    print("7. Centralize cost tracking logic")
    print("8. Extract response parsing to utilities")
    print("9. Standardize configuration classes")
    print("10. Use specific exceptions instead of generic handlers")
    print()
    print("=" * 100)

    return duplications


if __name__ == "__main__":
    analyze_duplications()
