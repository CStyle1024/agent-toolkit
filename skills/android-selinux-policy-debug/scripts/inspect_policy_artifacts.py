#!/usr/bin/env python3
"""Read extracted policy artifacts; report bytes/mappings, not effective permissions."""
import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def inspect(path, target_type, service):
    resolved = str(path.resolve())
    result = {"path": resolved}
    try:
        content = path.read_bytes()
    except OSError as exc:
        result.update(status="read_error", error=str(exc))
        return result
    result.update(
        status="read",
        size_bytes=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        type_name_occurrences=content.count(target_type.encode("ascii")),
    )
    # Contexts are separate text inputs; never interpret binary symbols as mappings.
    if service and (path.name == "service_contexts" or path.name.endswith("service_contexts")):
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            result["mapping_error"] = str(exc)
            return result
        matches = []
        for number, line in enumerate(text.splitlines(), 1):
            fields = line.split("#", 1)[0].split()
            if fields and fields[0] == service:
                context = fields[1] if len(fields) > 1 else None
                components = context.split(":", 3) if context else []
                context_type = components[2] if len(components) == 4 else None
                matches.append({
                    "line": number,
                    "context": context,
                    "context_type": context_type,
                    "matches_target_type": context_type == target_type,
                })
        # Preserve duplicates/mismatches so callers can diagnose them explicitly.
        result["exact_service_mappings"] = matches
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--type", required=True, dest="target_type", help="SELinux type name")
    parser.add_argument("--service", help="Exact Binder service name, for contexts files only")
    parser.add_argument("files", nargs="+", type=Path, help="Extracted policy/contexts files, not images")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", args.target_type):
        parser.error("--type must be an ASCII SELinux type identifier")
    records = [inspect(path, args.target_type, args.service) for path in args.files]
    groups = defaultdict(list)
    for record in records:
        if record["status"] == "read":
            if record["path"] not in groups[record["sha256"]]:
                groups[record["sha256"]].append(record["path"])
    output = {
        "target_type": args.target_type,
        "target_service": args.service,
        "files": records,
        "identical_file_groups": [paths for paths in groups.values() if len(paths) > 1],
        "limitations": [
            "Name occurrences are raw substring counts, not parsed type declarations or allow rules.",
            "Mappings are exact service-name rows from filenames ending in service_contexts.",
            "Identical hashes apply to sampled files, not whole images or runtime loading.",
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return int(any(r["status"] != "read" or "mapping_error" in r for r in records))


if __name__ == "__main__":
    sys.exit(main())
