#!/usr/bin/env python
"""
Fix import paths in agent subdirectories.

All files in agents/*/  need to use ... instead of .. to reach company_researcher/
"""

import re
from pathlib import Path

def fix_imports_in_file(filepath: Path) -> bool:
    """Fix relative imports in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Fix imports from parent (..X → ...X)
        # Match patterns like: from ..config import, from ..state import, etc.
        content = re.sub(
            r'from \.\.config import',
            'from ...config import',
            content
        )
        content = re.sub(
            r'from \.\.state import',
            'from ...state import',
            content
        )
        content = re.sub(
            r'from \.\.prompts import',
            'from ...prompts import',
            content
        )
        content = re.sub(
            r'from \.\.quality import',
            'from ...quality import',
            content
        )
        content = re.sub(
            r'from \.\.tools import',
            'from ...tools import',
            content
        )
        content = re.sub(
            r'from \.\.memory import',
            'from ...memory import',
            content
        )

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    """Fix imports in all agent subdirectory files."""
    project_root = Path(__file__).parent.parent
    agents_dir = project_root / 'src' / 'company_researcher' / 'agents'

    # Target subdirectories
    subdirs = ['financial', 'market', 'specialized', 'research']

    files_fixed = []

    for subdir in subdirs:
        subdir_path = agents_dir / subdir
        if not subdir_path.exists():
            continue

        print(f"\n[*] Processing {subdir}/...")

        for pyfile in subdir_path.glob('*.py'):
            if fix_imports_in_file(pyfile):
                print(f"  [+] Fixed: {pyfile.name}")
                files_fixed.append(pyfile)
            else:
                print(f"  [ ] No changes: {pyfile.name}")

    print(f"\n" + "=" * 60)
    print(f"[+] Fixed {len(files_fixed)} files")
    print("=" * 60)

    if files_fixed:
        print("\nFixed files:")
        for f in files_fixed:
            print(f"  - {f.relative_to(project_root)}")


if __name__ == '__main__':
    main()
