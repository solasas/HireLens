import os

# Settings() is constructed at import time (app.db.session, app.main). Make
# sure required env vars exist before any app module is imported, so the
# test suite never depends on a real .env file being present.
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("ENVIRONMENT", "test")
