
$files = Get-ChildItem -Path ".cursor/prompts/prompts/extracted" -Recurse -Filter "*.md"

foreach ($file in $files) {
    if ($file.Name -eq "README.md") {
        Write-Host "Skipping README.md"
        continue
    }
    $content = Get-Content -Path $file.FullName -Raw

    # Skip if already has front-matter
    if ($content -match '(?s)^\s*---\r?\n') {
        Write-Host "Skipping $($file.Name) - already has front-matter"
        continue
    }

    $name = $file.BaseName
    # Clean up name for ID (replace spaces with dashes, generic sanitization if needed)
    $idName = $name.ToLower()

    $frontMatter = @"
---
id: prompt.extracted.$idName.v1
kind: prompt
version: 1.0.0
description: Extracted prompt pattern for $name
provenance:
  owner: team-extraction
  last_review: 2025-12-06
---

"@

    $newContent = $frontMatter + $content
    Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8
    Write-Host "Updated $($file.Name)"
}
