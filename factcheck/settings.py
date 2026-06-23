BOT_NAME = "factcheck"

SPIDER_MODULES = ["factcheck.spiders"]
NEWSPIDER_MODULE = "factcheck.spiders"

# Vários sites de fact-checking bloqueiam crawlers que respeitam o robots.txt
# de forma estrita. Como o conteúdo é público, desabilitamos para viabilizar a
# coleta. (Pode ser religado em ROBOTSTXT_OBEY=True.)
ROBOTSTXT_OBEY = False

# Identificação de navegador para evitar bloqueios simples (ex.: HTTP 403).
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

# Coleta educada: pequena espera entre requisições + autothrottle.
DOWNLOAD_DELAY = 1
AUTOTHROTTLE_ENABLED = True

# Alguns sites (ex.: UOL) retornam 403 de forma intermitente por proteção
# anti-bot; tentamos novamente algumas vezes.
RETRY_TIMES = 4
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403]

# Reator asyncio é exigido pelo scrapy-playwright (spider lupa) e é seguro
# para os demais spiders.
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"

# Persistência no PostgreSQL.
ITEM_PIPELINES = {
    "factcheck.pipelines.PostgresPipeline": 300,
}
