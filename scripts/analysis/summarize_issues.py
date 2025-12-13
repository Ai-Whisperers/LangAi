#!/usr/bin/env python3
"""Summarize documentation issues by file and type."""

import json
from collections import defaultdict
from pathlib import Path

def main():
    with open('documentation_issues.json', 'r', encoding='utf-8') as f:
        issues = json.load(f)

    # Group by file
    by_file = defaultdict(list)
    for issue in issues:
        by_file[issue['file']].append(issue)

    # Group by type
    by_type = defaultdict(list)
    for issue in issues:
        by_type[issue['type']].append(issue)

    # Sort by number of issues
    sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)

    print('TOP 50 FILES WITH MOST DOCUMENTATION ISSUES')
    print('='*80)
    for i, (filepath, file_issues) in enumerate(sorted_files[:50], 1):
        # Get relative path
        rel_path = str(Path(filepath).relative_to(Path('c:/Users/Alejandro/Documents/Ivan/Work/Lang ai/src')))
        high = sum(1 for iss in file_issues if iss['severity'] == 'high')
        medium = sum(1 for iss in file_issues if iss['severity'] == 'medium')
        low = sum(1 for iss in file_issues if iss['severity'] == 'low')
        print(f'{i}. {rel_path}')
        print(f'   Total: {len(file_issues)} | High: {high}, Medium: {medium}, Low: {low}')
        print()

    print('\n\nISSUES BY TYPE')
    print('='*80)
    sorted_types = sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True)
    for issue_type, type_issues in sorted_types:
        high = sum(1 for iss in type_issues if iss['severity'] == 'high')
        medium = sum(1 for iss in type_issues if iss['severity'] == 'medium')
        low = sum(1 for iss in type_issues if iss['severity'] == 'low')
        print(f'{issue_type}: {len(type_issues)} total')
        print(f'  High: {high}, Medium: {medium}, Low: {low}')
        print()

if __name__ == '__main__':
    main()
