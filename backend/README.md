# Backend server for DiffKemp automation

Backend server which manages:

- automatic comparison of new versions or commits of projects,
- web interface for going through the results.

## Requirements / Dependencies

- `crontab`, Python 3.12+, bash, Podman

## Development

0. Install dependencies

1. Setup container used for project comparison:

   ```bash
   bash comparison_container/build.sh
   ```

2. Install project with dependencies

    ```bash
    virtualenv .venv --python /usr/bin/python3.12
    source .venv/bin/activate
    pip install -e .[dev]
    ```

3. Run initial comparison:

   ```bash
   diffkemp-automation-compare
   ```

4. After initial comparison is finished, setup automatic checking of new versions:

   ```bash
   backend/create_cron_job.sh
   ```

5. Running web server

   ```bash
   diffkemp-automation-dev-web
   ```

### Code style checking

```bash
flake8
isort .
mypy .
```

## Architecture notes

- The comparison is done in Podman container.
- The container is specified in `comparison_container/Dockerfile`.
- The container contains files from `comparison_container/files/` in `/runner/`
  directory, for more details see `comparison_container/files/README.md`.
