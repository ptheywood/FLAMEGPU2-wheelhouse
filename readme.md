# FLAME GPU 2 Wheelhouse

Repository for generating and hosting a python wheelhouse, for non pypi compliant wheels, for simpler installation of pyflamegpu

`main` contains:

+ `scripts/get_release_json.py` - uses `gh` to query the `FLAMEGPU/FLAMEGPU2` repository for releases and their assets, storing to JSON on disk
+ `scripts/build_wheelhouse.sh` - Generate a html file compliant with `pip install`'s `-f, --find-links <url>` option from the previously stored JSON

    ```text
    -f, --find-links <url>      If a URL or path to an html file, 
    then parse for links to archives such as sdist (.tar.gz) or wheel (.whl) files. 
    If a local path or file:// URL that's a directory, 
    then look for archives in the directory listing.
    Links to VCS project URLs are not supported.
    ```

Via GitHub actions, these scripts can be executed, and the resulting HTML file(s) committed to the `gh_pages` branch, making it publicly accessible on the internet.

## Dependencies

+ `python3` (>= 3.6)
+ `gh`

## Todo

+ [x] Implement basic `scripts/get_release_json.py`
+ [x] Implement basic `scripts/build_wheelhouse.py`
+ [ ] Implement CI
+ [ ] Decide on vis vs non-vis wheelhouse files?
+ [ ] Decide on hosting URI(s)
+ [ ] Decide on pre-release vs non-prelease wheel houses
+ [ ] Decide on caching/comitting of previously encountered release versions (to reduce gh API pressure)