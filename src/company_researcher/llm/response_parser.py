"""
Centralized LLM Response Parser.

This module provides utilities for parsing LLM responses,
eliminating duplicated JSON parsing logic across agent files.

Usage:
    from company_researcher.llm import parse_json_response, extract_json_block

    # Parse JSON from response
    data = parse_json_response(response_text, default={"queries": []})

    # Extract JSON from markdown blocks
    json_str = extract_json_block(response_text)
"""

import json
import re
from typing import Any, Dict, List, Optional, Union, TypeVar, Callable
from dataclasses import dataclass


T = TypeVar('T')


@dataclass
class ParseResult:
    """Result of parsing operation."""
    success: bool
    data: Any
    error: Optional[str] = None
    raw_text: Optional[str] = None


class ResponseParser:
    """
    Parser for LLM responses with JSON extraction capabilities.

    Handles common patterns:
    - JSON in markdown code blocks (```json ... ```)
    - Raw JSON responses
    - JSON with surrounding text
    - Malformed JSON with recovery attempts
    """

    # Patterns for JSON extraction
    JSON_BLOCK_PATTERN = re.compile(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', re.IGNORECASE)
    JSON_OBJECT_PATTERN = re.compile(r'\{[\s\S]*\}')
    JSON_ARRAY_PATTERN = re.compile(r'\[[\s\S]*\]')

    @classmethod
    def extract_json_block(cls, text: str) -> Optional[str]:
        """
        Extract JSON from markdown code block.

        Args:
            text: Raw response text

        Returns:
            Extracted JSON string or None
        """
        # Try markdown code blocks first
        match = cls.JSON_BLOCK_PATTERN.search(text)
        if match:
            return match.group(1).strip()

        # Try raw JSON object
        match = cls.JSON_OBJECT_PATTERN.search(text)
        if match:
            return match.group(0)

        # Try raw JSON array
        match = cls.JSON_ARRAY_PATTERN.search(text)
        if match:
            return match.group(0)

        return None

    @classmethod
    def parse_json(
        cls,
        text: str,
        default: Optional[T] = None,
        strict: bool = False
    ) -> Union[Dict, List, T]:
        """
        Parse JSON from LLM response text.

        Args:
            text: Raw response text
            default: Default value if parsing fails
            strict: If True, raise exception on failure

        Returns:
            Parsed JSON data or default value

        Raises:
            ValueError: If strict=True and parsing fails
        """
        if not text:
            if strict:
                raise ValueError("Empty response text")
            return default

        # Try direct parsing first
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        # Try extracting from code block
        json_str = cls.extract_json_block(text)
        if json_str:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Try fixing common issues
        fixed = cls._fix_json_issues(text)
        if fixed:
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass

        if strict:
            raise ValueError(f"Failed to parse JSON from response: {text[:200]}...")

        return default

    @classmethod
    def _fix_json_issues(cls, text: str) -> Optional[str]:
        """
        Attempt to fix common JSON formatting issues.

        Args:
            text: Potentially malformed JSON

        Returns:
            Fixed JSON string or None
        """
        # Remove BOM and common prefixes
        text = text.strip()
        text = text.lstrip('\ufeff')

        # Remove common response prefixes
        prefixes = ['Here is', 'Here\'s', 'The JSON', 'Response:', 'Output:']
        for prefix in prefixes:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
                # Remove colon if present
                text = text.lstrip(':').strip()

        # Try to find JSON boundaries
        json_str = cls.extract_json_block(text)
        if json_str:
            text = json_str

        # Fix trailing commas in objects
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)

        # Fix single quotes to double quotes (careful with apostrophes)
        # Only do this if there are no double quotes
        if '"' not in text and "'" in text:
            text = text.replace("'", '"')

        return text if text else None

    @classmethod
    def parse_with_schema(
        cls,
        text: str,
        schema: Dict[str, type],
        default: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Parse JSON and validate against a simple schema.

        Args:
            text: Raw response text
            schema: Dict mapping keys to expected types
            default: Default value if parsing fails

        Returns:
            Validated parsed data or default
        """
        data = cls.parse_json(text, default={})

        if not isinstance(data, dict):
            return default or {}

        # Validate schema
        for key, expected_type in schema.items():
            if key in data:
                if not isinstance(data[key], expected_type):
                    # Try type coercion
                    try:
                        data[key] = expected_type(data[key])
                    except (ValueError, TypeError):
                        if default and key in default:
                            data[key] = default[key]

        return data

    @classmethod
    def extract_list(
        cls,
        text: str,
        separator: str = '\n',
        filter_empty: bool = True
    ) -> List[str]:
        """
        Extract a list from text response.

        Handles:
        - Numbered lists (1., 2., etc.)
        - Bulleted lists (-, *, •)
        - JSON arrays
        - Newline-separated items

        Args:
            text: Raw response text
            separator: Fallback separator
            filter_empty: Remove empty items

        Returns:
            List of extracted items
        """
        # Try JSON array first
        try:
            data = cls.parse_json(text)
            if isinstance(data, list):
                return [str(item) for item in data if not filter_empty or item]
        except Exception:
            pass

        # Remove markdown code blocks
        text = cls.JSON_BLOCK_PATTERN.sub('', text)

        # Split by common list patterns
        lines = text.split('\n')
        items = []

        for line in lines:
            line = line.strip()

            # Remove list markers
            line = re.sub(r'^[\d]+[.)]\s*', '', line)  # Numbered
            line = re.sub(r'^[-*•]\s*', '', line)  # Bulleted
            line = line.strip()

            if line or not filter_empty:
                items.append(line)

        return items

    @classmethod
    def extract_sections(
        cls,
        text: str,
        section_pattern: str = r'^#{1,3}\s+(.+)$'
    ) -> Dict[str, str]:
        """
        Extract sections from markdown-formatted response.

        Args:
            text: Markdown text
            section_pattern: Regex pattern for section headers

        Returns:
            Dict mapping section titles to content
        """
        sections = {}
        current_section = None
        current_content = []

        for line in text.split('\n'):
            match = re.match(section_pattern, line, re.MULTILINE)
            if match:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                current_section = match.group(1).strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    @classmethod
    def extract_table(cls, text: str) -> List[Dict[str, str]]:
        """
        Extract data from markdown table.

        Args:
            text: Text containing markdown table

        Returns:
            List of dicts with table data
        """
        rows = []
        headers = []

        for line in text.split('\n'):
            line = line.strip()
            if not line.startswith('|'):
                continue

            # Skip separator rows
            if re.match(r'^\|[\s\-:|]+\|$', line):
                continue

            # Parse cells
            cells = [c.strip() for c in line.split('|')[1:-1]]

            if not headers:
                headers = cells
            else:
                row = dict(zip(headers, cells))
                rows.append(row)

        return rows

    @classmethod
    def extract_number(
        cls,
        text: str,
        pattern: Optional[str] = None,
        default: float = 0.0
    ) -> float:
        """
        Extract a number from text.

        Args:
            text: Text containing number
            pattern: Optional regex pattern with capture group
            default: Default value if not found

        Returns:
            Extracted number
        """
        if pattern:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except (ValueError, IndexError):
                    pass

        # Try common patterns
        patterns = [
            r'\$?([\d,]+\.?\d*)\s*(?:billion|B)',  # Billions
            r'\$?([\d,]+\.?\d*)\s*(?:million|M)',  # Millions
            r'\$?([\d,]+\.?\d*)\s*(?:thousand|K)',  # Thousands
            r'\$?([\d,]+\.?\d*)',  # Raw numbers
        ]

        multipliers = [1e9, 1e6, 1e3, 1]

        for pat, mult in zip(patterns, multipliers):
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1).replace(',', ''))
                    return value * mult
                except ValueError:
                    continue

        return default


# ============================================================================
# Module-level convenience functions
# ============================================================================

def parse_json_response(
    text: str,
    default: Optional[T] = None,
    strict: bool = False
) -> Union[Dict, List, T]:
    """
    Parse JSON from LLM response.

    Replaces the common pattern:
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            data = json.loads(content.strip())
        except json.JSONDecodeError:
            data = default_value

    With:
        data = parse_json_response(content, default=default_value)
    """
    return ResponseParser.parse_json(text, default, strict)


def extract_json_block(text: str) -> Optional[str]:
    """Extract JSON string from markdown code block."""
    return ResponseParser.extract_json_block(text)


def extract_list_from_response(
    text: str,
    filter_empty: bool = True
) -> List[str]:
    """Extract list items from response."""
    return ResponseParser.extract_list(text, filter_empty=filter_empty)


def extract_sections_from_response(text: str) -> Dict[str, str]:
    """Extract markdown sections from response."""
    return ResponseParser.extract_sections(text)


def extract_number_from_response(
    text: str,
    pattern: Optional[str] = None,
    default: float = 0.0
) -> float:
    """Extract number from response text."""
    return ResponseParser.extract_number(text, pattern, default)
