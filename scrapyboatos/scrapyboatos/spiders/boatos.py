import scrapy


class BoatosSpider(scrapy.Spider):
    name = "boatos"
    allowed_domains = ["www.boatos.org"]
    start_urls = ["https://www.boatos.org/"]

    count = 0
    max_count = 100

    def parse(self, response):
        if self.count >= self.max_count:
            return

        for manchete in response.css('.blog-entry-title a'):
            link = manchete.css('::attr(href)').get()

            if self.count < self.max_count:
                self.count += 1

            yield response.follow(link, self.parse_article)

        next_page = "https://www.boatos.org/?paged=" + str(self.count)
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        text = response.css('.nv-content-wrap p::text').getall()
        tag_index = text.index('Conclusão') + 1

        dados = {
            'link': response.url,
            'title': response.css('.nv-title-meta-wrap h1::text').get(),
            'author': response.css('.author-name a::text').get(),
            'data': response.css('.entry-date::text').get(),
            'text': ' '.join(response.css('.nv-content-wrap p::text').getall()),
            'tag': response.css('.nv-content-wrap p::text').getall()[tag_index]
        }

        yield dados
