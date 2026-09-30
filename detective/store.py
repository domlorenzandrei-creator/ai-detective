import sqlite3


class LogStore:
    def __init__(self, entries):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute(
            "CREATE TABLE access_log (person_id TEXT, room TEXT, minute INTEGER)"
        )
        self.conn.execute("CREATE INDEX idx_person_time ON access_log (person_id, minute)")
        self.conn.executemany("INSERT INTO access_log VALUES (?, ?, ?)", entries)
        self.conn.commit()

    def location_at(self, person_id, minute):
        row = self.conn.execute(
            "SELECT room FROM access_log "
            "WHERE person_id = ? AND minute <= ? "
            "ORDER BY minute DESC LIMIT 1",
            (person_id, minute),
        ).fetchone()
        return row[0] if row else None

    def history(self, person_id):
        return self.conn.execute(
            "SELECT room, minute FROM access_log WHERE person_id = ? ORDER BY minute",
            (person_id,),
        ).fetchall()