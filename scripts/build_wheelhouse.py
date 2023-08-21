#!/usr/bin/env python3

"""
Provided a path to a JSON file containing per release wheel names and URLS, output a html wheelhouse for pip consumption via -f, --find-links <url> or --extra-index-url <url>
"""

import argparse
import pathlib
import json
import re

def pep503_normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()

def cli():
    # CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-json", type=pathlib.Path, required=True, help="Path to json file containing a list of objects, one per release containing all artifacts for output")
    parser.add_argument("-o", "--output-dir", type=pathlib.Path, required=True, help="Path for html directory output")
    # add --many-wheelhouses/--no-many-wheelhouses, creating a directory / html file build per cuda version and per vis / non vis.
    parser.add_argument('--many-wheelhouses', default=True, action=argparse.BooleanOptionalAction, help="Enable/Disable creation of separate html files per local version component. Enabled by default")
    parser.add_argument("--baseurl", type=str, help="Base url to embed within the installation instructions. Include the trailing /.")
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
                is_vis = "-vis" if vis_match else ""
                subdir = f"{cuda_version}{is_vis}"
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

def write_project_list_to_disk(filepath, projects):
    a_list = [f"    <a href=\"{pep503_normalize(pname)}/\">{pname}</a>" for pname in projects]
    anchors = "<br />\n".join(a_list)
    html = f"""<!DOCTYPE html>
<html>
  <body>
    {anchors}
  </body>
</html>"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as fp:
        fp.write(html)


def write_installation_instructions(filepath, sample_package, descriptions):
    i_tr_list = []
    f_tr_list = []
    for desc, i_uri, f_uri in descriptions:
        i_tr_list.append(f"        <tr><td>{desc}/</td><td><code>python3 -m pip install --extra-index-url {i_uri} {sample_package}</code></td></tr>")
        f_tr_list.append(f"        <tr><td>{desc}/</td><td><code>python3 -m pip install --find-links {f_uri} {sample_package}</code></td></tr>")
    i_tablerows = "\n".join(i_tr_list)
    f_tablerows = "\n".join(f_tr_list)
    html = f"""<!DOCTYPE html>
<html>
  <head>
  <title>pyflamegpu wheels</title>
  </head>
  <body>
    <h1><code>pyflamegpu</code> Wheels</h1>
    <p><code>pyflamegpu</code> wheels can be installed via pip using the <code>--extra-index-url<code> or <code>-f, --find-links</code> arguments, and one of the uri's provided.<p>
    <h2>Using <code>--extra-index-url<code></h2>
    <table style="text-align:left;">
        <tr>
            <th>Description</th>
            <th>Command</th>
        </tr>
        {i_tablerows}
    </table>
    <h2>Using <code>-f, --find-links</code></h2>
    <table style="text-align:left;">
        <tr>
            <th>Description</th>
            <th>Command</th>
        </tr>
        {f_tablerows}
    </table>
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
    # @todo - this might need to be dynamic for a0 vis wheels 
    projects = ["pyflamegpu"]
    whl_subdir = "whl"
    whl_dir = args.output_dir / whl_subdir
    descriptions = []

    # Write the main wheelhouse to disk
    uri_base = f"{whl_subdir}"
    if args.baseurl is not None and len(args.baseurl) > 0:
        uri_base = f"{args.baseurl}/{whl_subdir}" if not args.baseurl.endswith("/") else f"{args.baseurl}{whl_subdir}"
    write_project_list_to_disk(whl_dir / "index.html", projects)
    write_anchor_list_to_disk(whl_dir / projects[0] / "index.html", full_a_list)
    descriptions.append([
        f"All builds of {projects[0]}. Defaults to latest CUDA with visualisation",
        f"{uri_base}/",
        f"{uri_base}/{projects[0]}/",
    ])
    # Write each child wheelhouse to disk
    cuda_re = re.compile(r"cuda([0-9]{2})([0-9])")
    for subdir in sorted(split_files_a_list_dict.keys(), reverse=True):
        sub_a_list = split_files_a_list_dict[subdir]
        write_project_list_to_disk(whl_dir / subdir / "index.html", projects)
        write_anchor_list_to_disk(whl_dir / subdir / projects[0] / "index.html", sub_a_list)
        cuda_match = cuda_re.search(subdir)
        cuda_ver = f"with CUDA {cuda_match.group(1)}.{cuda_match.group(2)}" if cuda_match else ""
        vis = "with visualisation" if "vis" in subdir else "without visualistion"
        descriptions.append([
            f"{projects[0]} built {cuda_ver} {vis}",
            f"{uri_base}/{subdir}/",
            f"{uri_base}/{subdir}/{projects[0]}/",
        ])

    # Write the root index with some installation instructions
    write_installation_instructions(args.output_dir / "index.html", projects[0], descriptions)

if __name__ == "__main__":
    main()