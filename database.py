# -*- coding: utf-8 -*-
# Marusya - database
import sqlite3
from typing import Literal, Optional


class Database:
    SQLS = (
        'CREATE TABLE IF NOT EXISTS "photos" ("id" INTEGER PRIMARY KEY, "category" INTEGER)',
    )

    def __init__(self) -> None:
        pass

    def _create_tables(self) -> None:
        db = sqlite3.connect('skill.db')
        for sql in self.SQLS:
            db.execute(sql)
        db.commit()

    def add_photo(self, id: int, category: int) -> Literal[True]:
        db = sqlite3.connect('skill.db')
        db.execute('INSERT INTO photos VALUES (?,?)', (id, category))
        db.commit()
        return True

    def get_category_photo(self, category: int) -> Optional[int]:
        db = sqlite3.connect('skill.db')
        cur = db.execute('SELECT id FROM photos WHERE category=?', (category,))
        fetch = cur.fetchone()
        if fetch:
            return fetch[0]
        return None
