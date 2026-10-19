CREATE TABLE IF NOT EXISTS export_cursors (
    export_id TEXT PRIMARY KEY,
    last_row_id BIGINT NOT NULL DEFAULT 0
);
