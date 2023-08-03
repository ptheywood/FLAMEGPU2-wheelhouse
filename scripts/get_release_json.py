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
    
    # use gh to query the repo for a list of releases
    gh_list_releases_command = f"gh api -X GET repos/{GHREPO}/releases --jq '[ .[]|.tag_name ]'"
    gh_list_releases = subprocess.run(gh_list_releases_command, shell=True, capture_output=True)
    if gh_list_releases.returncode != 0:
        raise Exception(f"Error occured while fetching list of releases {gh_list_releases.stderr.decode()}")
    releases_list = json.loads(gh_list_releases.stdout.decode())

    # for each release, query gh for the assets and build the output data structure
    data = []
    for idx, tag in enumerate(releases_list):
        # escaping needed here is kinda grim
        gh_list_assets_command = f'gh -R {GHREPO} release view {tag} --json assets --jq "[ .assets.[] | select(.name|endswith(\\".whl\\")) | {{name,url}} ]"'
        # print(gh_list_assets_command)
        gh_list_assets = subprocess.run(gh_list_assets_command, shell=True, capture_output=True)
        if gh_list_assets.returncode != 0:
            raise Exception(f"Error occured while fetching list of releases {gh_list_assets.stderr.decode()}")
        release_assets = json.loads(gh_list_assets.stdout.decode())
        release_obj = {
            "release": tag, 
            "wheels": release_assets
        }
        data.append(release_obj)

    # output json data to disk
    with open(args.json_path, "w") as fp:
        json.dump(data, fp, indent=4)


if __name__ == "__main__":
    main()