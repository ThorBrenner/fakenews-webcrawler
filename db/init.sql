-- Esquema do banco de dados das agências de fact-checking.
-- Executado automaticamente pelo Postgres na primeira inicialização
-- (montado em /docker-entrypoint-initdb.d).

-- Tabela de fontes: identifica de qual agência cada notícia veio.
CREATE TABLE IF NOT EXISTS sources (
    id          SERIAL PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    base_url    TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tabela principal com os metadados das notícias / checagens.
CREATE TABLE IF NOT EXISTS news (
    id            SERIAL PRIMARY KEY,
    source_id     INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    spider        TEXT,
    link          TEXT UNIQUE NOT NULL,
    title         TEXT,
    author        TEXT,
    published_raw TEXT,          -- data publicada (texto bruto extraído do site)
    text          TEXT,
    tag           TEXT,
    fact          TEXT,          -- afirmação verificada (aosfatos)
    fact_check    TEXT,          -- veredito/checagem (aosfatos)
    subject       TEXT,          -- assunto (lupa)
    collected_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_news_source_id ON news (source_id);
CREATE INDEX IF NOT EXISTS idx_news_collected_at ON news (collected_at);

-- Pré-cadastro das agências (idempotente).
INSERT INTO sources (name, base_url) VALUES
    ('G1 Fato ou Fake', 'https://g1.globo.com/fato-ou-fake/'),
    ('UOL Confere',     'https://noticias.uol.com.br/confere/'),
    ('Lupa',            'https://lupa.uol.com.br/'),
    ('Boatos.org',      'https://www.boatos.org/'),
    ('Aos Fatos',       'https://www.aosfatos.org/')
ON CONFLICT (name) DO NOTHING;
