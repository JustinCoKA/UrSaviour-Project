Migration: add `jobNumber` INT AUTO_INCREMENT to `etlJobs`

What this migration does:
- Adds a new column `jobNumber` to `etlJobs`.
- Backfills sequential integer values for existing rows.
- Marks `jobNumber` as NOT NULL and adds a unique index.
- (MySQL only) converts `jobNumber` to AUTO_INCREMENT and sets the next auto value.

How to run (recommended):
1) Backup your DB. Important: this migration changes schema and adds AUTO_INCREMENT.
2) From `backend/` run alembic:
   alembic -c db/migrations/alembic.ini upgrade head

Notes and rollback:
- The downgrade drops `jobNumber` column.
- If your DB is not MySQL, the backfill SQL may need adjustments (ROW_NUMBER portability). Review the migration file before running.

If you want, I can instead add a separate `jobNumber` column without AUTO_INCREMENT and let app-side backfill/assign it; that is safer for some environments.
