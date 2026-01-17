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

3. Prepare DB:

   ```bash
   alembic upgrade head
   ```

4. Run initial comparison:

   ```bash
   diffkemp-automation-compare
   ```

5. After initial comparison is finished, setup automatic checking of new versions:

   ```bash
   backend/create_cron_job.sh
   ```

6. Prepare `.env` file, create it based on `.env.example`

7. Running web server

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
- For DB is used [SQLite](https://sqlite.org/), [SqlAlchemy](https://www.sqlalchemy.org/)
  is used for ORM. For DB scheme migration is used [Alembic](https://alembic.sqlalchemy.org/en/latest/).
- For logging in is used [GitHub App](https://docs.github.com/en/apps/creating-github-apps/writing-code-for-a-github-app/building-a-login-with-github-button-with-a-github-app).
