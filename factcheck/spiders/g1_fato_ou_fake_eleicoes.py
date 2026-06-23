import scrapy

from factcheck.items import NewsItem


class G1FatoOuFakeEleicoesSpider(scrapy.Spider):
    name = "g1_fato_ou_fake_eleicoes"
    allowed_domains = ["g1.globo.com"]
    start_urls = ["https://g1.globo.com/fato-ou-fake/eleicoes/"]

    count = 0
    max_count = 400

    def parse(self, response):
        if self.count >= self.max_count:
            return

        for manchete in response.css('.feed-post-body-title a'):
            link = manchete.css('::attr(href)').get()

            if self.count < self.max_count:
                self.count += 1

            yield response.follow(link, self.parse_article)

        next_page = response.css('.load-more a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        # Veredito do G1 vem como hashtag em negrito (ex.: #FAKE, #FATO).
        strong_text = ' '.join(response.css('.content-text__container strong::text').getall())
        hashtags = [w.strip('.,;:!?') for w in strong_text.split() if w.startswith('#')]
        tag = ' '.join(dict.fromkeys(h for h in hashtags if h))

        yield NewsItem(
            link=response.url,
            title=response.css('.content-head__title::text').get(),
            author=' '.join(response.css('.content-publication-data__from::text').getall()),
            data=response.css('.content-publication-data__updated time::text').get(),
            text=' '.join(response.css('.content-text__container::text').getall()),
            tag=tag or None,
        )
