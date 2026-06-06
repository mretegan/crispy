#!/usr/bin/env python3
"""Submit the built Windows installer to VirusTotal for an antivirus scan.

Run in CI after PyInstaller and Inno Setup. It is a no-op (exit 0) when the
VT_API_KEY environment variable is unset, mirroring the macOS codesign.sh and
notarize.sh scripts. Uploading uses the official vt-py client, which handles
VirusTotal's large-file (>32 MB) upload flow transparently. On a release build
the permanent report link is also appended to the GitHub release notes.
"""

import glob
import hashlib
import json
import os
import sys
import urllib.request


def sha256(path):
    """Return the SHA-256 of a file, read in chunks to bound memory use."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_to_release_notes(line):
    """Add ``line`` to the GitHub release notes when run on a release event."""
    if os.environ.get("GITHUB_EVENT_NAME") != "release":
        return
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    tag = os.environ.get("GITHUB_REF_NAME")
    if not (token and repo and tag):
        return

    api = f"https://api.github.com/repos/{repo}/releases"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    def call(url, method="GET", payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    release = call(f"{api}/tags/{tag}")
    body = release.get("body") or ""
    if line in body:  # idempotent if the step is re-run
        return
    call(f"{api}/{release['id']}", "PATCH", {"body": f"{body.rstrip()}\n\n{line}\n"})
    print("Added the VirusTotal report link to the release notes.")


def main():
    api_key = os.environ.get("VT_API_KEY", "")
    if not api_key:
        print("Skipping VirusTotal scan; VT_API_KEY is not set.")
        return

    import vt  # imported here so the skip path needs no extra dependency

    matches = sorted(glob.glob(os.path.join("package", "artifacts", "*.exe")))
    if not matches:
        sys.exit("No installer found at package/artifacts/*.exe")
    installer = matches[0]
    name = os.path.basename(installer)

    # The report lives permanently at the file's SHA-256, independent of the
    # one-off analysis id, which makes it a stable link for the release notes.
    report = f"https://www.virustotal.com/gui/file/{sha256(installer)}"

    print(f"Uploading {name} to VirusTotal...")
    with vt.Client(api_key) as client, open(installer, "rb") as f:
        client.scan_file(f)  # vt-py uses the upload-URL endpoint for >32 MB files
    print(f"Submitted. Report: {report}")

    note = f"VirusTotal scan of `{name}`: {report}"
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as fh:
            fh.write(note + "\n")
    append_to_release_notes(note)


if __name__ == "__main__":
    main()
