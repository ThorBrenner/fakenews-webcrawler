# Fake News Webcrawler

Coletores (spiders Scrapy) para agências de fact-checking brasileiras,
dockerizados em um único `docker-compose`. A cada execução diária, os
metadados das notícias/checagens são persistidos em um banco PostgreSQL
organizado.

## Agências e spiders

Tudo vive em **um único projeto Scrapy** (`factcheck/`), com um spider
especializado por site:

| Agência (`sources`) | Spider |
|---------------------|--------|
| G1 Fato ou Fake     | `g1_fato_ou_fake`, `g1_fato_ou_fake_eleicoes` |
| UOL Confere         | `uol_confere` |
| Lupa                | `lupa` (usa Playwright, configurado via `custom_settings`) |
| Boatos.org          | `boatos` |
| Aos Fatos           | `aosfatos` |

## Estrutura

```
fakenews-webcrawler/
  scrapy.cfg
  factcheck/
    settings.py        # configuração única (ITEM_PIPELINES, reator asyncio)
    items.py           # NewsItem padronizado
    pipelines.py       # PostgresPipeline + mapa spider -> agência
    spiders/           # um spider por agência
  run_all.py           # roda todos os spiders em sequência
  scheduler.py         # agenda a coleta diária
  db/init.sql          # schema do banco
  Dockerfile
  docker-compose.yml
  requirements.txt
```

## Arquitetura

- **`db`** — PostgreSQL. O schema é criado automaticamente na primeira subida
  a partir de `db/init.sql`.
- **`crawler`** — imagem única com o projeto Scrapy. O `scheduler.py`
  dispara `run_all.py` (todos os spiders) uma vez por dia.

### Banco de dados

Duas tabelas:

- **`sources`** — identifica a agência de origem (`id`, `name`, `base_url`).
- **`news`** — metadados das notícias, com `source_id` referenciando a fonte:
  `link` (único), `title`, `author`, `published_raw`, `text`, `tag`, `fact`,
  `fact_check`, `subject`, `spider`, `collected_at`.

A coluna `link` é única, então execuções diárias não duplicam notícias já
coletadas (`ON CONFLICT DO NOTHING`).

## Como usar

Pré-requisito: Docker e Docker Compose.

```bash
cd fakenews-webcrawler
cp .env.example .env   # opcional, para ajustar credenciais/horário
docker compose up -d --build
```

- Por padrão (`RUN_ON_START=true`) uma coleta roda logo ao subir.
- Depois, a coleta ocorre todo dia no horário definido em `CRAWL_TIME` (UTC).

Acompanhar logs:

```bash
docker compose logs -f crawler
```

Consultar os dados:

```bash
docker compose exec db psql -U factcheck -d factcheck \
  -c "SELECT s.name, count(*) FROM news n JOIN sources s ON s.id = n.source_id GROUP BY s.name;"
```

Rodar a coleta manualmente (sem esperar o horário):

```bash
docker compose exec crawler python run_all.py
```

## Configuração (variáveis de ambiente)

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | `factcheck` | Credenciais do banco |
| `CRAWL_TIME` | `03:00` | Horário da coleta diária (HH:MM, UTC) |
| `RUN_ON_START` | `true` | Coletar imediatamente ao subir o container |
