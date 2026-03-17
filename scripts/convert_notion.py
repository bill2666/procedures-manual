"""
convert_notion.py — Notion → MkDocs Material post-processor
 
Runs after Make.com commits markdown files to the repo but before
MkDocs builds the site. Transforms Notion-specific patterns into
MkDocs Material syntax.
 
Main conversions:
  1. Notion callout blocks (blockquotes with emoji) → MkDocs admonitions
  2. Cleanup of any Notion export artefacts
 
Usage:
  python scripts/convert_notion.py
  (Processes all .md files in the docs/ directory in-place)
"""
 
import re
import os
import glob
 
# ---------------------------------------------------------------------------
# Emoji → admonition type mapping
# ---------------------------------------------------------------------------
CALLOUT_MAP = {
    # Tips / ideas
    "💡": "tip",
    "✅": "success",
    "🎯": "tip",
    # Warnings / caution
    "⚠️": "warning",
    "⚠": "warning",
    "🔧": "warning",
    # Danger / critical
    "❗": "danger",
    "❌": "danger",
    "🔴": "danger",
    "🛑": "danger",
    # Info / context
    "ℹ️": "info",
    "ℹ": "info",
    "📝": "info",
    "📌": "info",
    # Notes
    "📎": "note",
    "🗒️": "note",
    "💬": "note",
    # Examples
    "📋": "example",
    # Questions
    "❓": "question",
    # Bugs
    "🐛": "bug",
    "🪲": "bug",
}
 
# Build a regex pattern that matches any of the mapped emoji
# at the start of a blockquote line
EMOJI_PATTERN = "|".join(re.escape(e) for e in CALLOUT_MAP.keys())
 
 
def convert_callouts(content: str) -> str:
    """
    Convert Notion-style callout blocks to MkDocs admonitions.
 
    Notion callouts come through as blockquotes like:
        > ⚠️ **SendKeys is fragile.** It depends on window focus...
        > More content on next line.
 
    or sometimes:
        > ⚠️ Content without bold title
 
    Converts to:
        !!! warning "SendKeys is fragile."
            It depends on window focus...
            More content on next line.
    """
    lines = content.split("\n")
    result = []
    i = 0
 
    while i < len(lines):
        line = lines[i]
 
        # Check if this line starts a callout blockquote
        match = re.match(
            rf"^>\s*({EMOJI_PATTERN})\s*(.*)", line
        )
 
        if match:
            emoji = match.group(1)
            first_line_content = match.group(2).strip()
            admonition_type = CALLOUT_MAP.get(emoji, "note")
 
            # Try to extract a bold title from the first line
            # Pattern: **Title text.** rest of content
            title_match = re.match(
                r"\*\*(.+?)\*\*\s*(.*)", first_line_content
            )
 
            if title_match:
                title = title_match.group(1).rstrip(".")
                remaining = title_match.group(2).strip()
                result.append(f'!!! {admonition_type} "{title}"')
                if remaining:
                    result.append(f"    {remaining}")
            elif first_line_content:
                # No bold title — use the content as-is, no custom title
                result.append(f"!!! {admonition_type}")
                result.append(f"    {first_line_content}")
            else:
                result.append(f"!!! {admonition_type}")
 
            # Collect continuation lines (subsequent > lines)
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                continuation = re.sub(r"^>\s?", "", lines[i])
                result.append(f"    {continuation}")
                i += 1
 
            # Add a blank line after the admonition block
            result.append("")
            continue
 
        result.append(line)
        i += 1
 
    return "\n".join(result)
 
 
def fix_code_language_tags(content: str) -> str:
    """
    Map code block language tags that Notion uses to ones Pygments recognises.
 
    Notion lets you type any language name, but Pygments has specific lexer
    names. This maps common mismatches.
    """
    LANGUAGE_MAP = {
        "vba":       "vb.net",
        "VBA":       "vb.net",
        "dax":       "text",      # No Pygments lexer for DAX; plain text
        "DAX":       "text",
        "m":         "text",      # Power Query M has no Pygments lexer
        "powerquery": "text",
    }
 
    def replace_lang(match):
        prefix = match.group(1)   # ``` or ``` with spaces
        lang = match.group(2)     # the language tag
        rest = match.group(3)     # anything after (e.g. title="...")
        mapped = LANGUAGE_MAP.get(lang, lang)
        return f"{prefix}{mapped}{rest}"
 
    # Match opening code fences with a language tag
    # e.g. ```vba or ```vba title="something"
    content = re.sub(
        r"(```\s*)(\w[\w.]*)(.*)",
        replace_lang,
        content
    )
 
    return content
 
 
def clean_notion_artefacts(content: str) -> str:
    """
    Remove or fix common Notion export artefacts.
    """
    # Remove Notion's sometimes-added HTML comments
    content = re.sub(r"<!--\s*notionvc:.*?-->", "", content)
 
    # Fix double-blank-lines (Notion sometimes adds extras)
    content = re.sub(r"\n{4,}", "\n\n\n", content)
 
    return content
 
 
def process_file(filepath: str) -> bool:
    """
    Process a single markdown file. Returns True if changes were made.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()
 
    processed = original
    processed = convert_callouts(processed)
    processed = fix_code_language_tags(processed)
    processed = clean_notion_artefacts(processed)
 
    if processed != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(processed)
        return True
    return False
 
 
def main():
    """
    Process all markdown files in the docs/ directory.
    """
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    docs_dir = os.path.abspath(docs_dir)
 
    md_files = glob.glob(os.path.join(docs_dir, "**", "*.md"), recursive=True)
 
    changed = 0
    for filepath in md_files:
        if process_file(filepath):
            rel_path = os.path.relpath(filepath, docs_dir)
            print(f"  ✓ Converted: {rel_path}")
            changed += 1
 
    print(f"\nProcessed {len(md_files)} files, {changed} modified.")
 
 
if __name__ == "__main__":
    main()
