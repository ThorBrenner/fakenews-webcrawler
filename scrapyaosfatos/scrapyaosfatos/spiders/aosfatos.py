import scrapy

class AosfatosSpider(scrapy.Spider):
    name = "aosfatos"
    #allowed_domains = ["aosfatos.com"]
    start_urls = ["https://www.aosfatos.org/noticias/?formato=checagem"]

    count = 0
    max_count = 400

    def parse(self, response):
        if self.count >= self.max_count:
            return

        for manchete in response.css('.grid'):
            link = manchete.css('div a::attr(href)').get()

            if self.count < self.max_count:
                self.count += 1

            yield response.follow(link, self.parse_article)

        next_page = response.css('.text-center a::attr(href)').getall()[-1]
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        dados = {
            'link': response.url,
            'title': response.css('.prose h1::text').get(),
            'data': response.css('.prose aside::text').get(),
            'author': response.css('.prose aside::text').getall()[6],
            'text': ' '.join(response.css('.mb-11 p::text').getall()).replace('\r\n', ''),
            'fact': response.css('.prose blockquote p::text').get() or response.css('.prose blockquote::text').get(),
            'check': ' '.join(response.css('.mb-11 details p::text').getall()),
            'tag': response.css('.prose blockquote::attr(data-stamp)').get()
        }
        yield dados