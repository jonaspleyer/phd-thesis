# PhD Thesis
This repository contains all files required to build my PhD Thesis.

## Building
The document depends on multiple submodules which need to be properly initialized before building
it.
Use the commands provided by the `Makefile` under `written/Makefile` to build the document.

```bash
# Builds Document
make
# Clean Artifacts
make clean
# Clean + Build
make fresh
# zip contents into archive for distribution
make zip
```
