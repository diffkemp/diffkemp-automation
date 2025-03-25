# DiffKemp Automation

Project that automatically executes DiffKemp on:

- **new releases** of certain projects
  -- it compares them with previous versions and provides web interface for
  viewing the results,
- **certain commits** of projects -- it compares them with codebase before the
  commit.

This should enable to DiffKemp developer:

- find unexpected semantic changes in the analyzed projects,
- find cases that DiffKemp does not handle correctly yet.

## Requirements

This project uses submodules/sub-projects, you need to run:

```bash
git submodule update --init --recursive
```

## Specification of projects

Projects which should be regularly compared are specified in
`backend/automation/configs/` dir. To add more projects or update the existing
see the `backend/automation/configs/README.md` doc.
