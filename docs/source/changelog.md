# Changelog

## 1.7 Poetry and Documentation

- Use `poetry` to manage dependencies
- Move documentation to [maltego-trx.readthedocs.io](https://maltego-trx.readthedocs.io).
- Drop `python3.6` support due to EOL.

## 1.6 Generate `.mtz` files for local transforms

Automatically generate am .mtz for your local transforms

## 1.5 Better XML Serialization

### 1.5.2

- Add logging output for invalid / missing params in xml serialization

### 1.5.1

- Add ignored files to starter and use README for pypi

### 1.5.0

- XML Serialization via `ElementTree` instead of string interpolation

## 1.4 Transform Registry

**1.4.0 and 1.4.1 are incompatible with python3.7 and lower.**

### 1.4.4

- Added skeletons for csv export in template dir
- made project.py application import compatible with docs

### 1.4.3

- GitHub Workflows for testing
- `TransformRegistry` typing
- Updates for the deployment examples

### 1.4.2

- Fixed python3.6 incompatibility