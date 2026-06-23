"""Pipeline de persistência no PostgreSQL.

Grava cada item na tabela ``news`` e garante que a agência (fonte)
correspondente exista na tabela ``sources``. As credenciais do banco vêm
de variáveis de ambiente definidas no docker-compose.
"""

import os

import psycopg2
from itemadapter import ItemAdapter

# Mapeia cada spider para a agência (fonte) à qual pertence.
SPIDER_SOURCE_MAP = {
    "g1_fato_ou_fake": {"name": "G1 Fato ou Fake", "base_url": "https://g1.globo.com/fato-ou-fake/"},
    "g1_fato_ou_fake_eleicoes": {"name": "G1 Fato ou Fake", "base_url": "https://g1.globo.com/fato-ou-fake/eleicoes/"},
    "uol_confere": {"name": "UOL Confere", "base_url": "https://noticias.uol.com.br/confere/"},
    "lupa": {"name": "Lupa", "base_url": "https://lupa.uol.com.br/"},
    "boatos": {"name": "Boatos.org", "base_url": "https://www.boatos.org/"},
    "aosfatos": {"name": "Aos Fatos", "base_url": "https://www.aosfatos.org/"},
}


class PostgresPipeline:
    def open_spider(self, spider):
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "db"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "factcheck"),
            user=os.getenv("POSTGRES_USER", "factcheck"),
            password=os.getenv("POSTGRES_PASSWORD", "factcheck"),
        )
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

        source = SPIDER_SOURCE_MAP.get(
            spider.name, {"name": spider.name, "base_url": None}
        )
        self.cur.execute(
            """
            INSERT INTO sources (name, base_url)
            VALUES (%s, %s)
            ON CONFLICT (name) DO UPDATE SET base_url = EXCLUDED.base_url
            RETURNING id
            """,
            (source["name"], source["base_url"]),
        )
        self.source_id = self.cur.fetchone()[0]

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        self.cur.execute(
            """
            INSERT INTO news (
                source_id, spider, link, title, author,
                published_raw, text, tag, fact, fact_check, subject
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (link) DO NOTHING
            """,
            (
                self.source_id,
                spider.name,
                adapter.get("link"),
                adapter.get("title"),
                adapter.get("author"),
                adapter.get("data"),
                adapter.get("text"),
                adapter.get("tag"),
                adapter.get("fact"),
                adapter.get("check"),
                adapter.get("subject"),
            ),
        )
        return item

    def close_spider(self, spider):
        if getattr(self, "cur", None):
            self.cur.close()
        if getattr(self, "conn", None):
            self.conn.close()
