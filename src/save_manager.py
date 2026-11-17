import sqlite3
from pathlib import Path


class SaveManager:
    """Local profile storage, isolated so it can be replaced on other platforms."""
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS players (username TEXT PRIMARY KEY, high_score INTEGER NOT NULL DEFAULT 0, highest_level INTEGER NOT NULL DEFAULT 1, games_played INTEGER NOT NULL DEFAULT 0)')

    def load(self, username):
        with sqlite3.connect(self.path) as db:
            db.execute('INSERT OR IGNORE INTO players (username) VALUES (?)', (username,))
            row = db.execute('SELECT high_score, highest_level, games_played FROM players WHERE username = ?', (username,)).fetchone()
        return {'high_score': row[0], 'highest_level': row[1], 'games_played': row[2]}

    def save_round(self, username, score, unlocked_level):
        with sqlite3.connect(self.path) as db:
            db.execute('UPDATE players SET high_score = MAX(high_score, ?), highest_level = MAX(highest_level, ?), games_played = games_played + 1 WHERE username = ?', (score, unlocked_level, username))
        return self.load(username)
