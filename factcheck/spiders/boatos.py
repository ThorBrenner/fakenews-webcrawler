import scrapy

from factcheck.items import NewsItem


class BoatosSpider(scrapy.Spider):
    name = "boatos"
    allowed_domains = ["www.boatos.org"]
    start_urls = ["https://www.boatos.org/"]

    count = 0
    max_count = 400

    def parse(self, response):
        if self.count >= self.max_count:
            return

        for manchete in response.css('.blog-entry-title a'):
            link = manchete.css('::attr(href)').get()

            # Ignora as versões traduzidas (não têm a seção "Conclusão").
            if not link or '/english/' in link or '/espanol/' in link:
                continue

            if self.count < self.max_count:
                self.count += 1

            yield response.follow(link, self.parse_article)

        pages = response.css('.page-numbers a::attr(href)').getall()
        if pages:
            yield response.follow(pages[-1], self.parse)

    def parse_article(self, response):
        paragraphs = response.css('.nv-content-wrap p::text').getall()

        # A "tag" é o parágrafo logo após a linha "Conclusão"; alguns posts
        # (ex.: versões em inglês/espanhol) não têm essa seção.
        tag = None
        if 'Conclusão' in paragraphs:
            tag_index = paragraphs.index('Conclusão') + 1
            if tag_index < len(paragraphs):
                tag = paragraphs[tag_index]

        yield NewsItem(
            link=response.url,
            title=response.css('.nv-title-meta-wrap h1::text').get(),
            author=response.css('.author-name a::text').get(),
            data=(response.css('time::attr(datetime)').get()
                  or response.css('time::text').get()
                  or response.css('.entry-date::text').get()),
            text=' '.join(paragraphs),
            tag=tag,
        )
