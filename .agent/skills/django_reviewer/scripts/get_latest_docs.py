#!/usr/bin/env python3
"""Resolve likely documentation URLs for Python packages via PyPI metadata."""

import sys
import json
import urllib.request
import re

def get_pypi_data(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return data
    except Exception:
        return None

def find_doc_url(pypi_data):
    if not pypi_data or 'info' not in pypi_data:
        return None

    info = pypi_data['info']
    urls = []

    # Check project_urls
    if 'project_urls' in info and info['project_urls']:
        for key, value in info['project_urls'].items():
            if re.search(r'doc|document|wiki|guide', key, re.IGNORECASE):
                return value
            urls.append(value)

    # Check home_page
    if 'home_page' in info and info['home_page']:
        return info['home_page']

    return urls[0] if urls else None

def main():
    if len(sys.argv) < 2:
        print("Usage: python get_latest_docs.py <package1> <package2> ...")
        sys.exit(1)

    packages = sys.argv[1:]
    results = {}

    for pkg in packages:
        data = get_pypi_data(pkg)
        url = find_doc_url(data)
        if url:
            results[pkg] = url
        else:
            results[pkg] = "Docs not found via PyPI"

    # Output simple text format for the agent to read
    for pkg, url in results.items():
        print(f"{pkg}: {url}")

if __name__ == "__main__":
    main()
