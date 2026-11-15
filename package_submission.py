"""
Packaging script for FinReg AI (Dvara Group Task 6 RAG Pipeline).
Creates the final compliant submission ZIP: <USN>_Task6.zip.
Excludes virtual environment, node_modules, backups, secrets, and temporary cache files.
"""

import os
import re
import sys
import zipfile
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Directory exclusions (filtered in-place by directory name)
EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "node_modules",
    "backups",
    ".agents",
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".idea",
    ".vscode",
    ".vite-temp"
}

# Exact filename exclusions (secrets and OS metadata)
EXCLUDE_FILES = {
    ".env",
    ".DS_Store",
    "Thumbs.db"
}

# File extension exclusions
EXCLUDE_EXTS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".bak"
}

def validate_usn(usn: str) -> str:
    """
    Validates that the provided USN is non-empty and strictly alphanumeric.
    Prevents path traversal, directory injection, and malformed archive names.
    """
    if not usn or not isinstance(usn, str):
        print("ERROR: USN cannot be empty.", file=sys.stderr)
        sys.exit(1)

    usn_clean = usn.strip().upper()

    if not usn_clean:
        print("ERROR: USN cannot be blank.", file=sys.stderr)
        sys.exit(1)

    if not re.match(r"^[A-Z0-9]+$", usn_clean):
        print(
            f"ERROR: Invalid USN '{usn}'. USN must contain only alphanumeric characters (A-Z, 0-9). "
            f"Spaces, slashes, backslashes, dots, and special characters are strictly prohibited.",
            file=sys.stderr
        )
        sys.exit(1)

    return usn_clean

def create_submission_zip(usn: str, output_dir: Path = BASE_DIR.parent, dry_run: bool = False):
    usn_clean = validate_usn(usn)
    zip_name = f"{usn_clean}_Task6.zip"
    zip_path = output_dir / zip_name

    action_label = "Simulating (DRY RUN)" if dry_run else "Creating"
    print(f"{action_label} submission archive: {zip_path}...")
    file_count = 0
    total_uncompressed_bytes = 0
    packaged_files = []

    for root, dirs, files in os.walk(BASE_DIR):
        # Prune excluded directories in-place by directory name
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            # Exclude sensitive secrets and OS metadata files
            if file in EXCLUDE_FILES:
                continue

            file_path = Path(root) / file

            # Exclude unwanted extensions
            if file_path.suffix in EXCLUDE_EXTS:
                continue

            # Exclude the zip archive itself if present in workspace
            if file == zip_name:
                continue

            rel_path = file_path.relative_to(BASE_DIR)
            file_size = file_path.stat().st_size
            file_count += 1
            total_uncompressed_bytes += file_size
            packaged_files.append((str(rel_path).replace("\\", "/"), file_size))

    uncompressed_mb = total_uncompressed_bytes / (1024 * 1024)
    print(f"\n==================================================")
    print(f"{'PREVIEW ONLY (No zip created)' if dry_run else 'Submission archive successfully created!'}")
    print(f"Archive Name: {zip_name}")
    if not dry_run:
        print(f"Location:     {zip_path}")
    print(f"Total Files:  {file_count} files selected")
    print(f"Total Size:   {uncompressed_mb:.2f} MB (uncompressed)")
    print(f"==================================================")

    if dry_run:
        return packaged_files

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for rel_str, _ in packaged_files:
            file_path = BASE_DIR / rel_str
            archive_name = Path(f"{usn_clean}_Task6") / rel_str
            zipf.write(file_path, arcname=str(archive_name))

    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"ZIP Size:     {zip_size_mb:.2f} MB (compressed)")

    # Verification: test reading the zip archive
    print("\nVerifying archive integrity...")
    with zipfile.ZipFile(zip_path, "r") as test_zip:
        bad_file = test_zip.testzip()
        if bad_file:
            print(f"WARNING: Corrupt file detected in zip: {bad_file}")
        else:
            print("Archive integrity check PASSED! (0 corrupt files)")

    return zip_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Package FinReg AI submission zip.")
    parser.add_argument(
        "--usn",
        type=str,
        required=True,
        help="Your University Seat Number (USN), e.g. --usn 01FE23BCS276"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview files to be packaged without creating the zip archive."
    )
    args = parser.parse_args()
    create_submission_zip(args.usn, dry_run=args.preview)
