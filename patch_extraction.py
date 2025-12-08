"""Patch extraction patterns in run_research.py"""
import re

# Read the file
with open('run_research.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace CEO section using regex
# Find pattern: from "# CEO / General Manager" to "# CFO" section
ceo_section_pattern = r'''(        # CEO / General Manager \(LATAM often uses GM instead of CEO\)
        ceo_patterns = \[
            # Direct title patterns.*?
        \]
        for pattern in ceo_patterns:
            match = re\.search\(pattern, report_text\)
            if match:
                name = match\.group\(1\)\.strip\(\)
                if is_valid_exec_name\(name\):
                    metrics\["leadership"\]\["ceo"\] = name
                    break)'''

new_ceo_section = '''        # Helper to clean executive names (remove garbage text)
        def clean_exec_name(name):
            if not name:
                return None
            # Strip whitespace and newlines
            name = name.strip()
            # Remove everything after newlines
            name = name.split('\\n')[0].strip()
            # Remove trailing parenthetical content
            name = re.sub(r'\\s*\\([^)]*\\)\\s*$', '', name)
            # Remove trailing role descriptions
            name = re.sub(r'\\s+(?:the|as|is|was|since|from).*$', '', name, flags=re.I)
            return name.strip()

        # CEO / General Manager (LATAM often uses GM instead of CEO)
        ceo_patterns = [
            # Markdown formatted (highest priority) - "**CEO:** Name"
            r'\\*\\*CEO\\*\\*[:\\s]+([A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+(?:\\s+[A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\\']+)+)',
            r'\\*\\*(?:General\\s+Manager|GM)[^*]*\\*\\*[:\\s]+([A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+(?:\\s+[A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\\']+)+)',
            # Direct title patterns
            r'(?:CEO|Chief\\s+Executive\\s+Officer)[:\\s,]+([A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+(?:\\s+[A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\\']+)+)',
            r'(?:General\\s+Manager|GM|Director\\s+General|Gerente\\s+General)[^:]*[:\\s,]+([A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+(?:\\s+[A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\\']+)+)',
            # Name followed by title
            r'([A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+(?:\\s+[A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\\']+)+)[,\\s]+(?:the\\s+)?(?:current\\s+)?(?:CEO|General\\s+Manager)',
            r'([A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+(?:\\s+[A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\\']+)+)\\s+(?:is\\s+)?(?:the\\s+)?(?:CEO|General\\s+Manager)',
            # Appointment patterns
            r'([A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+(?:\\s+[A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\\']+)+)\\s+(?:was\\s+)?appointed\\s+(?:as\\s+)?(?:CEO|General\\s+Manager|GM)',
            r'([A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+(?:\\s+[A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\\']+)+)\\s+(?:serves?|leads?|heads?)\\s+as\\s+(?:CEO|General\\s+Manager)',
            # Led by patterns
            r'(?:led\\s+by|headed\\s+by)\\s+(?:CEO\\s+)?([A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+(?:\\s+[A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\\']+)+)',
            # Parent company CEO pattern
            r'(?:Parent\\s+Company\\s+)?CEO[:\\s]+([A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1]+(?:\\s+[A-Z][a-z\u00e1\u00e9\u00ed\u00f3\u00fa\u00f1\\']+)+)',
        ]
        for pattern in ceo_patterns:
            match = re.search(pattern, report_text)
            if match:
                name = clean_exec_name(match.group(1))
                if name and is_valid_exec_name(name):
                    metrics["leadership"]["ceo"] = name
                    break'''

# Use a simpler approach - find the start and end markers
start_marker = '        # CEO / General Manager (LATAM often uses GM instead of CEO)'
end_marker = '\n\n        # CFO'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx > 0 and end_idx > start_idx:
    # Extract and replace
    old_section = content[start_idx:end_idx]
    content = content[:start_idx] + new_ceo_section + content[end_idx:]
    print(f"Replaced CEO section ({len(old_section)} chars -> {len(new_ceo_section)} chars)")
else:
    print(f"Could not find markers: start={start_idx}, end={end_idx}")

# Write back
with open('run_research.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
