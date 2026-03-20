#!/usr/bin/env python3
"""
Verify that PDF preprocessing produces correct line breaks in HTML output.

This script takes a preprocessed markdown file (output of Step 2), runs pandoc
on it, and checks that key sections have proper <br> tags instead of being
collapsed into single paragraphs.

Usage:
    python verify_linebreaks.py /tmp/ld-pdf-AccountName.md

Exit code 0 = all checks pass, 1 = failures found.
"""

import subprocess
import sys
import re
import os
import tempfile


def run_pandoc(md_path):
    """Convert markdown to HTML via pandoc and return the HTML string."""
    result = subprocess.run(
        ["pandoc", md_path, "-f", "markdown", "-t", "html5", "--standalone"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"FAIL: pandoc error: {result.stderr}")
        sys.exit(1)
    return result.stdout


def check_intro_linebreaks(html):
    """
    Check that the intro section (AE, SE, Deal Type, Next Call, etc.)
    has <br /> tags between fields, not collapsed into one paragraph.

    Expected: <strong>AE:</strong> value<br />\n<strong>SE:</strong> value<br />
    Bad: <strong>AE:</strong> value <strong>SE:</strong> value (all in one line)
    """
    failures = []

    # Find the paragraph containing the intro fields
    # Look for the pattern where AE and SE appear in the same <p> block
    intro_pattern = r'<p>.*?<strong>AE:</strong>.*?</p>'
    match = re.search(intro_pattern, html, re.DOTALL)

    if not match:
        # AE might not be present — check for SE or Deal Type
        intro_pattern = r'<p>.*?<strong>SE:</strong>.*?</p>'
        match = re.search(intro_pattern, html, re.DOTALL)

    if not match:
        failures.append("SKIP: No intro section found (no AE/SE fields)")
        return failures

    intro_block = match.group(0)

    # Count how many bold labels are in this block
    bold_labels = re.findall(r'<strong>[^<]+:</strong>', intro_block)

    if len(bold_labels) >= 2:
        # Check that there are <br /> tags between them
        br_count = intro_block.count('<br')
        if br_count < len(bold_labels) - 1:
            failures.append(
                f"FAIL: Intro section has {len(bold_labels)} fields but only "
                f"{br_count} line breaks. Expected at least {len(bold_labels) - 1}. "
                f"Fields are collapsed into a single paragraph."
            )
        else:
            print(f"  PASS: Intro section has {len(bold_labels)} fields with {br_count} line breaks")

    return failures


def check_callout_linebreaks(html, section_name, expected_fields):
    """
    Check that a summary callout block has <br /> tags between bullet items.

    Each > - **Field:** value line should produce a separate line in the HTML,
    not be collapsed into a single paragraph.
    """
    failures = []

    # Find the blockquote following the section heading
    # Pattern: <h2>section_name</h2> ... <blockquote> ... </blockquote>
    section_pattern = (
        rf'<h2[^>]*>[^<]*{re.escape(section_name)}[^<]*</h2>'
        r'.*?<blockquote>(.*?)</blockquote>'
    )
    match = re.search(section_pattern, html, re.DOTALL)

    if not match:
        failures.append(f"SKIP: No blockquote found after {section_name} heading")
        return failures

    blockquote = match.group(1)

    # Count bold field labels inside the blockquote
    bold_fields = re.findall(r'<strong>[^<]+:</strong>', blockquote)

    if expected_fields > 0 and len(bold_fields) < expected_fields:
        failures.append(
            f"FAIL: {section_name} callout has only {len(bold_fields)} bold fields, "
            f"expected at least {expected_fields}"
        )
        return failures

    if len(bold_fields) <= 1:
        print(f"  PASS: {section_name} callout has {len(bold_fields)} field(s) (single-line summary, no breaks needed)")
        return failures

    # Check for line breaks between fields
    br_count = blockquote.count('<br')

    # We need at least (number of fields - 1) line breaks for fields on separate lines
    # The summary title line also needs a break before the first field
    min_breaks = len(bold_fields) - 1

    if br_count < min_breaks:
        failures.append(
            f"FAIL: {section_name} callout has {len(bold_fields)} fields but only "
            f"{br_count} line breaks. Expected at least {min_breaks}. "
            f"Summary fields are collapsed into a single paragraph."
        )
    else:
        print(f"  PASS: {section_name} callout has {len(bold_fields)} fields with {br_count} line breaks")

    # Additional check: look for items that are truly collapsed —
    # where a "- <strong>" appears WITHOUT a preceding <br> tag.
    # Note: "- <strong>" with a preceding <br> is fine (that's the expected format).
    collapsed = re.findall(r'(?<!<br />)\n?\s*-\s*<strong>', blockquote)
    # Filter out the very first bullet (which follows the title line with <br>)
    if collapsed:
        # Check if each occurrence has a <br> before it
        true_collapsed = []
        for m in re.finditer(r'-\s*<strong>', blockquote):
            # Look back from the match position for a <br
            before = blockquote[:m.start()]
            # Check if there's a <br in the last ~20 chars before this match
            if '<br' not in before[-30:]:
                true_collapsed.append(m.group())
        if true_collapsed:
            failures.append(
                f"FAIL: {section_name} callout has {len(true_collapsed)} collapsed bullet items "
                f"(found '- <strong>' pattern without preceding line break)"
            )

    return failures


def check_com_callout(html):
    """
    Check Command of the Message summary callout.
    This uses **Before:**, **Pain:**, **Required:**, **After:** format
    (not bulleted like MEDDPICC).
    """
    failures = []

    section_pattern = (
        r'<h2[^>]*>[^<]*Command of the Message[^<]*</h2>'
        r'.*?<blockquote>(.*?)</blockquote>'
    )
    match = re.search(section_pattern, html, re.DOTALL)

    if not match:
        failures.append("SKIP: No Command of the Message callout found")
        return failures

    blockquote = match.group(1)
    bold_fields = re.findall(r'<strong>[^<]+:</strong>', blockquote)

    if len(bold_fields) >= 2:
        br_count = blockquote.count('<br')
        if br_count < len(bold_fields) - 1:
            failures.append(
                f"FAIL: Command of the Message callout has {len(bold_fields)} fields "
                f"but only {br_count} line breaks. Fields are collapsed."
            )
        else:
            print(f"  PASS: CoM callout has {len(bold_fields)} fields with {br_count} line breaks")

    return failures


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_linebreaks.py <preprocessed-markdown-file>")
        print("       python verify_linebreaks.py --check-html <html-file>")
        sys.exit(1)

    if sys.argv[1] == "--check-html":
        with open(sys.argv[2], "r") as f:
            html = f.read()
    else:
        md_path = sys.argv[1]
        if not os.path.exists(md_path):
            print(f"File not found: {md_path}")
            sys.exit(1)
        html = run_pandoc(md_path)

    all_failures = []

    print("Checking line breaks in HTML output...\n")

    # 1. Intro section
    print("[Intro Section]")
    all_failures.extend(check_intro_linebreaks(html))

    # 2. MEDDPICC summary callout (8 fields)
    print("[MEDDPICC Summary]")
    all_failures.extend(check_callout_linebreaks(html, "MEDDPICC", 6))

    # 3. Command of the Message summary
    print("[Command of the Message]")
    all_failures.extend(check_com_callout(html))

    # 4. TECHMAPS summary callout (8 fields)
    print("[TECHMAPS Summary]")
    all_failures.extend(check_callout_linebreaks(html, "TECHMAPS", 5))

    # 5. Tech Stack summary callout (may be a single-line summary, so 0 is OK)
    print("[Tech Stack Summary]")
    all_failures.extend(check_callout_linebreaks(html, "Tech Stack", 0))

    # Report
    print()
    real_failures = [f for f in all_failures if f.startswith("FAIL")]
    skips = [f for f in all_failures if f.startswith("SKIP")]

    if skips:
        print(f"Skipped: {len(skips)}")
        for s in skips:
            print(f"  {s}")

    if real_failures:
        print(f"\n{'='*60}")
        print(f"FAILED: {len(real_failures)} check(s)")
        print(f"{'='*60}")
        for f in real_failures:
            print(f"  {f}")
        sys.exit(1)
    else:
        print(f"\n{'='*60}")
        print(f"ALL CHECKS PASSED")
        print(f"{'='*60}")
        sys.exit(0)


if __name__ == "__main__":
    main()
