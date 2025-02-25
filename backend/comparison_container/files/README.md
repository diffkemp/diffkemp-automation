# Container files

This directory contains files that are copied to the comparison container to a `/runner` directory.

## Content

```txt
.
├── build_diffkemp.sh - Script for building DiffKemp.
├── flake.nix - Definition of flake dev shell with additional dependencies.
├── get_diffkemp_bin.sh - Script prints a path to DiffKemp binary.
├── get_diffkemp_sha.sh - Script prints SHA of current commit.
├── README.md - This file.
└── version_comparison - Scripts for comparison of project versions.
    ├── build_view_files.sh - Creates visualisation of found differences
    |                         for individual projects' versions.
    ├── version-analysis - A sub-project for analysis of project's versions.
    └── run_cmp.sh - Script launches the comparison.
```
