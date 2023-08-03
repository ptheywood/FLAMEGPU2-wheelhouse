#!/usr/bin/env python3

"""
Provided a path to a JSON file containing per release wheel names and URLS, output a html wheelhouse for pip consumption via -f, --find-links <url>
@todo - filter vis / non-vis wheels?
@todo - output as cli arg rather than using stdout?
@todo - multiple html files in one pass? 
@todo - split by cuda version? 
"""

import argparse
import pathlib
import json

def main():
    # CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-json", type=pathlib.Path, required=True, help="Path to json file containing a list of objects, one per release containing all artifacts for output")
    parser.add_argument("-o", "--output-html", type=pathlib.Path, required=False, help="Path for html file output")
    args = parser.parse_args()

    # Validate CLI
    if not args.input_json.is_file():
        raise Exception(f"{args.input_json} is not a valid file")
    
    if args.output_html is not None and args.output_html.is_dir():
        raise Exception(f"{args.output_html} is an existing directory")

    a_list = []
    # Load the json from disk into memory
    with open(args.input_json, "r") as fp: 
        data = json.load(fp)
        # build a list of <a> elements in order of release (reverse chrono?)
        for idx, release_obj in enumerate(data):
            if "release" not in release_obj or "wheels" not in release_obj:
                raise Exception(f"Invalid JSON data - 'release' or 'wheels' missing from {idx}th list element")
            release_tag = release_obj["release"]
            for wheel_obj in release_obj["wheels"]:
                wheel_name = wheel_obj["name"]
                wheel_url = wheel_obj["url"]
                a_list.append(f"        <a href=\"{wheel_url}\">{wheel_name}</a>")

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

    # Output the html to disk or stdout depending on cli usage.
    if args.output_html is not None:
        with open(args.output_html, "w") as fp:
            fp.write(html)
    else:
        print(html)
            

if __name__ == "__main__":
    main()