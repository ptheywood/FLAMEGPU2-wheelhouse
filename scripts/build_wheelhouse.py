#!/usr/bin/env python3

"""
Provided a path to a JSON file containing per release wheel names and URLS, output a html wheelhouse for pip consumption via -f, --find-links <url>
"""

import argparse
import pathlib
import json
import re

def cli():
    # CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-json", type=pathlib.Path, required=True, help="Path to json file containing a list of objects, one per release containing all artifacts for output")
    parser.add_argument("-o", "--output-dir", type=pathlib.Path, required=True, help="Path for html directory output")
    # add --many-wheelhouses/--no-many-wheelhouses, creating a directory / html file build per cuda version and per vis / non vis.
    parser.add_argument('--many-wheelhouses', default=True, action=argparse.BooleanOptionalAction, help="Enable/Disable creation of separate html files per local version component. Enabled by default")
    args =  parser.parse_args()

    # Validate CLI
    if not args.input_json.is_file():
        raise Exception(f"{args.input_json} is not a valid file")
    
    if args.output_dir is not None and args.output_dir.is_file():
        raise Exception(f"{args.output_dir} is an existing file. Please specify a directory or unused path")

    return args

def load(args):
    # Load the json from disk into memory
    with open(args.input_json, "r") as fp: 
        return json.load(fp)

def build_full_anchor_list(args, data):
    # Build a list of anchor elements for each wheel in all releases
    full_a_list = []
    for idx, release_obj in enumerate(data):
        if "release" not in release_obj or "wheels" not in release_obj:
            raise Exception(f"Invalid JSON data - 'release' or 'wheels' missing from {idx}th list element")
        release_tag = release_obj["release"]
        for wheel_obj in release_obj["wheels"]:
            wheel_name = wheel_obj["name"]
            wheel_url = wheel_obj["url"]
            full_a_list.append(f"        <a href=\"{wheel_url}\">{wheel_name}</a>")
    return full_a_list

def build_split_files_anchor_list(args, data):
    # Build a dict grouping the wheels by cuda version and / or vis status.
    split_files_dict = {}
    if args.many_wheelhouses:
        cuda_version_re = re.compile(r"(cuda[0-9]{3})")
        vis_re = re.compile(r"vis")
        for idx, release_obj in enumerate(data):
            if "release" not in release_obj or "wheels" not in release_obj:
                raise Exception(f"Invalid JSON data - 'release' or 'wheels' missing from {idx}th list element")
            release_tag = release_obj["release"]
            for wheel_obj in release_obj["wheels"]:
                wheel_name = wheel_obj["name"]
                wheel_url = wheel_obj["url"]
                cuda_match = cuda_version_re.search(wheel_name)
                cuda_version = cuda_match.group(0) if cuda_match else "cuda110" # only version without an explicit cuda version is cuda 11.0 as of rc0. This might need adjusting in the future
                vis_match = vis_re.search(wheel_name)
                is_vis = "vis" if vis_match else ""
                subdir = pathlib.Path(cuda_version) / is_vis
                if subdir not in split_files_dict:
                    split_files_dict[subdir] = []
                split_files_dict[subdir].append(f"        <a href=\"{wheel_url}\">{wheel_name}</a>")
    return split_files_dict

def write_anchor_list_to_disk(filepath, a_list):
        # Join th elist of anchors with line breaks and new lines
        anchors = "<br />\n".join(a_list)
        # Create the final html output
        html = f"""<!DOCTYPE html>
<html>
    <body>
        <h1>pyflamegpu wheel urls</h1>
{anchors}
    </body>
</html>"""

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as fp:
            fp.write(html)

def main():
    # Parse CLI
    args = cli()
    # Load data from disk
    data = load(args)
    # Build list of anchors for the "main" wheelhouse
    full_a_list = build_full_anchor_list(args, data)
    # Build dictionary of anchors for each "split wheelhouse" 
    split_files_a_list_dict = build_split_files_anchor_list(args, data)
    # Write the main wheelhouse to disk
    write_anchor_list_to_disk(args.output_dir / "index.html", full_a_list)
    # Write each child wheelhouse to disk
    for subdir, sub_a_list in split_files_a_list_dict.items():
        write_anchor_list_to_disk(args.output_dir / subdir / "index.html", sub_a_list)

if __name__ == "__main__":
    main()