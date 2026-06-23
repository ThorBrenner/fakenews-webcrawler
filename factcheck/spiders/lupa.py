import re

import scrapy
from scrapy_playwright.page import PageMethod

from factcheck.items import NewsItem

# URLs de artigos seguem o padrão /jornalismo/AAAA/MM/DD/slug (estável, ao
# contrário das classes CSS ofuscadas que mudam a cada deploy do site).
ARTICLE_RE = re.compile(r"/jornalismo/20\d{2}/\d{2}/\d{2}/")


class LupaSpider(scrapy.Spider):
    name = "lupa"
    # A listagem fica em lupa.uol.com.br e os artigos redirecionam para
    # agencialupa.org; ambos os domínios são permitidos.
    allowed_domains = ["agencialupa.org", "lupa.uol.com.br"]

    # Configuração do Playwright isolada neste spider, para não afetar os demais.
    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 90000,
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    }

    count = 0
    max_count = 400

    # Scrapy 2.13+ usa o método assíncrono start() no lugar de start_requests().
    async def start(self):
        yield scrapy.Request(
            "https://lupa.uol.com.br/jornalismo/categoria/checagem",
            self.parse,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "a[href*='/jornalismo/20']", timeout=90000),
                ],
            },
        )

    def parse(self, response):
        seen = set()
        for href in response.css("a[href*='/jornalismo/']::attr(href)").getall():
            if not ARTICLE_RE.search(href) or href in seen:
                continue
            seen.add(href)

            if self.count >= self.max_count:
                return
            self.count += 1

            yield response.follow(
                href,
                self.parse_article,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "article p", timeout=90000),
                    ],
                },
            )

    def parse_article(self, response):
        # O espaço antes de ::text captura também o texto de nós aninhados.
        paragraphs = [t.strip() for t in response.css("article p ::text").getall() if t.strip()]
        authors = response.css("a[href*='/autor']::text").getall()
        title = " ".join(t.strip() for t in response.css("h1 ::text").getall() if t.strip())
        date = " ".join(t.strip() for t in response.css("time ::text").getall() if t.strip())

        # Veredito/rótulo (ex.: FALSO, VERDADEIRO). Artigos antigos podem não ter.
        verdict = (
            response.css(".custom-block-default .block-text strong::text").get()
            or response.css(".custom-block-default .block-text::text").get()
        )

        yield NewsItem(
            link=response.url,
            title=title or None,
            data=date or None,
            author=", ".join(dict.fromkeys(a.strip() for a in authors if a.strip())) or None,
            text=" ".join(paragraphs),
            tag=verdict.strip() if verdict else None,
        )
