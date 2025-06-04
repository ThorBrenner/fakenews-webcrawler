import scrapy


class G1Spider(scrapy.Spider):
    name = "g1"
    allowed_domains = ["g1.globo.com"]
    start_urls = ["https://g1.globo.com/"]

    count = 0
    max_count = 400

    def parse(self, response):
        if self.count >= self.max_count:
            return

        for manchete in  response.css('.feed-media-wrapper a'):
            link = manchete.css('::attr(href)').get()

            if self.count < self.max_count:
                self.count += 1

            yield response.follow(link, self.parse_article)

        next_page = response.css('.load-more a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        dados = {
            'link': response.url,
            'title': response.css('.content-head__title::text').get(),
            'author': response.css('.content-publication-data__from::text').get(),
            'data': response.css('.content-publication-data__updated time::text').get(),
            'text': ' '.join(response.css('.content-text__container::text').getall()),
            'tag': '#FATO'
        }

        yield dados
