#!/usr/bin/env python3

"""
Query the github API via `gh` for FLAMEGPU/FLAMEGPU2 releases and their artifacts. Stores relevant data to disk in a JSON data structure.
@todo - if the provided json path is an existing json file, modify it with fresh data rather than starting again (unless another cli option is provided)
"""

import argparse
import pathlib
import json
import subprocess
import os

# Github repository to query
GHREPO = "FLAMEGPU/FLAMEGPU2"

def main():
    # CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", type=pathlib.Path, help="Path to json file to store queried data in")
    args = parser.parse_args()

    # Validate CLI
    if args.json_path.is_dir():
        raise Exception(f"{args.json_path} is a directory, provide an existing file path, or an unused path")

    # validate the gh is available on the cli
    gh_check = subprocess.run(["gh"], shell=True, capture_output=True)
    if gh_check.returncode != 0:
        raise Exception(f"Error occurred checking 'gh' usage. Please install 'gh' and ensure it is on your path")
    
    # use gh to query the repo for releases including assets. 
    # --paginate means if more than one api call is needed it will make it.
    # Use jq to select non-draft releases, and filter output to include the name of the release, and the per asset name and url.
    # Note the split jq string to avoid escaping braces
    jq_command = "'[ .[] | select(.draft==false) | {release: .tag_name, wheels: [.assets[] | {name:.name, url:.browser_download_url } ] } ]'"
    gh_list_releases_command = f"gh api -X GET repos/{GHREPO}/releases --paginate --jq {jq_command}"
    gh_list_releases = subprocess.run(gh_list_releases_command, shell=True, capture_output=True)
    if gh_list_releases.returncode != 0:
        raise Exception(f"Error occured while fetching list of releases {gh_list_releases.stderr.decode()}")
    data = json.loads(gh_list_releases.stdout.decode())

    # output json data to disk
    with open(args.json_path, "w") as fp:
        json.dump(data, fp, indent=4)


if __name__ == "__main__":
    main()