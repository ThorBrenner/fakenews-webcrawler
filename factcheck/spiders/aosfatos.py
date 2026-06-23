import scrapy

from factcheck.items import NewsItem


class AosfatosSpider(scrapy.Spider):
    name = "aosfatos"
    # allowed_domains = ["aosfatos.com"]
    start_urls = ["https://www.aosfatos.org/noticias/?formato=checagem"]

    count = 0
    max_count = 400

    def parse(self, response):
        if self.count >= self.max_count:
            return

        for manchete in response.css('.grid'):
            link = manchete.css('div a::attr(href)').get()

            # Só segue páginas de checagem (/noticias/<slug>/), evitando
            # paginação (/noticias/?...) e páginas institucionais.
            if not link or '/noticias/' not in link or '?' in link:
                continue

            if self.count < self.max_count:
                self.count += 1

            yield response.follow(link, self.parse_article)

        pages = response.css('.text-center a::attr(href)').getall()
        if pages:
            yield response.follow(pages[-1], self.parse)

    def parse_article(self, response):
        title = response.css('.prose h1::text').get()

        # Alguns links seguidos não são artigos (ex.: "/sobre", páginas de tag);
        # sem título, não há o que persistir.
        if not title:
            return

        # A aside tem a forma: ["<data>", ",", "<hora>", "Por", "<autor>", ...].
        asides = [t.strip() for t in response.css('.prose aside::text').getall() if t.strip()]

        author = None
        if 'Por' in asides:
            i = asides.index('Por')
            if i + 1 < len(asides):
                author = asides[i + 1]

        # Data = tudo que vem antes do "Por" (juntando dia e hora).
        date_parts = []
        for t in asides:
            if t == 'Por':
                break
            if t != ',':
                date_parts.append(t)
        data = ' '.join(date_parts) or None

        yield NewsItem(
            link=response.url,
            title=title,
            data=data,
            author=author,
            text=' '.join(response.css('.mb-11 p::text').getall()).replace('\r\n', ''),
            fact=response.css('.prose blockquote p::text').get() or response.css('.prose blockquote::text').get(),
            check=' '.join(response.css('.mb-11 details p::text').getall()),
            tag=response.css('.prose blockquote::attr(data-stamp)').get(),
        )
