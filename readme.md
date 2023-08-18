# FLAME GPU 2 Wheelhouse

Repository for generating and hosting a python wheelhouse, for non pypi compliant wheels, for simpler installation of `pyflamegpu`.

`main` contains:

+ `scripts/get_release_json.py` - uses `gh` to query the `FLAMEGPU/FLAMEGPU2` repository for releases and their assets, storing to JSON on disk
+ `scripts/build_wheelhouse.py` - Generate a html files compliant with `pip install`'s `-f, --find-links <url>`, `-i, --index-url <url>` & `--extra-index-url <url>` options from the previously stored JSON

    ```text
    -i, --index-url <url>       Base URL of the Python Package Index (default https://pypi.org/simple). This should
                                point to a repository compliant with PEP 503 (the simple repository API) or a local
                                directory laid out in the same format.
    --extra-index-url <url>     Extra URLs of package indexes to use in addition to --index-url. Should follow the same
                                rules as --index-url.
    --no-index                  Ignore package index (only looking at --find-links URLs instead).
    -f, --find-links <url>      If a URL or path to an html file, then parse for links to archives such as sdist
                                (.tar.gz) or wheel (.whl) files. If a local path or file:// URL that's a directory, then
                                look for archives in the directory listing. Links to VCS project URLs are not supported.
    ```

Via GitHub actions, these scripts can be executed, and the resulting HTML file(s) deployed to gh pages, making it publicly accessible on the internet.

## Dependencies

+ `python3` (>= 3.6)
+ `gh`, with sufficient privileges
+ Internet connection

## Usage

```bash
# via gh, get release and asset info, storing into pyflamegpu.json
./scripts/get_release_json.py pyflamegpu.json
# Generate html containing links to each gh hosted wheel, into _build
./scripts/builds_wheelhouse.py -i pyflamegpu.json -o sample/wheelhouse
```

It is then possible to install pyflamegpu and specific versions via pip using `-f, --find-links <url>`, `-i, --index-url <url>` & `--extra-index-url <url>`

I.e. Using the version hosted at [`whl.flamegpu.com`](https://whl.flamegpu.com) via `-i, --index-url`

```bash
# Install the "newest" version, so most recent with newest CUDA and with visualiastion, via -f
python3 -m pip install --index-url https://whl.flamegpu.com/whl/ pyflamegpu
# Install a specific version, with the most recent CUDA available and with visualisation
python3 -m pip install --index-url https://whl.flamegpu.com/whl/ pyflamegpu==2.0.0rc0
# Install the most recent non-visualisation build, using a specific cuda version, in this case CUDA 11.2
python3 -m pip install --index-url https://whl.flamegpu.com/whl/cuda112/ pyflamegpu
# Install the most recent visualisation build, using a specific cuda version, in this case CUDA 11.0
python3 -m pip install --index-url https://whl.flamegpu.com/whl/cuda110-vis/ pyflamegpu
```

Or using the version hosted at [`whl.flamegpu.com`](https://whl.flamegpu.com) via `-f, --find-links`

```bash
# Install the "newest" version, so most recent with newest CUDA and with visualiastion, via -f
python3 -m pip install -f https://whl.flamegpu.com/whl/pyflamegpu/ pyflamegpu
# Install a specific version, with the most recent CUDA available and with visualisation
python3 -m pip install -f https://whl.flamegpu.com/whl/pyflamegpu/ pyflamegpu==2.0.0rc0
# Install the most recent non-visualisation build, using a specific cuda version, in this case CUDA 11.2
python3 -m pip install -f https://whl.flamegpu.com/whl/cuda112/pyflamegpu/ pyflamegpu
# Install the most recent visualisation build, using a specific cuda version, in this case CUDA 11.0
python3 -m pip install -f https://whl.flamegpu.com/whl/cuda110-vis/pyflamegpu/ pyflamegpu
```


Or using a local copy of the wheelhouse via `-i, --index-url`

```bash
# Install the "newest" version, so most recent with newest CUDA and with visualiastion, via -f
python3 -m pip install --index-url sample/wheelhouse/whl/ pyflamegpu
# Install a specific version, with the most recent CUDA available and with visualisation
python3 -m pip install --index-url sample/wheelhouse/whl/ pyflamegpu==2.0.0rc0
# Install the most recent non-visualisation build, using a specific cuda version, in this case CUDA 11.2
python3 -m pip install --index-url sample/wheelhouse/whl/cuda112/ pyflamegpu
# Install the most recent visualisation build, using a specific cuda version, in this case CUDA 11.0
python3 -m pip install --index-url sample/wheelhouse/whl/cuda110-vis/ pyflamegpu
```

Or using a local copy of the wheelhouse via `-f, --find-links`

```bash
# Install the "newest" version, so most recent with newest CUDA and with visualiastion, via -f
python3 -m pip install -f sample/wheelhouse/whl/pyflamegpu/ pyflamegpu
# Install a specific version, with the most recent CUDA available and with visualisation
python3 -m pip install -f sample/wheelhouse/whl/pyflamegpu/ pyflamegpu==2.0.0rc0
# Install the most recent non-visualisation build, using a specific cuda version, in this case CUDA 11.2
python3 -m pip install -f sample/wheelhouse/whl/cuda112/pyflamegpu/ pyflamegpu
# Install the most recent visualisation build, using a specific cuda version, in this case CUDA 11.0
python3 -m pip install -f sample/wheelhouse/whl/cuda110-vis/pyflamegpu/ pyflamegpu
```

## CI

The included ci workflow runs the included scripts, and on certain events deploys to gh pages.
