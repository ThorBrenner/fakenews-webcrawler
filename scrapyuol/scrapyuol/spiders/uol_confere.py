import scrapy
import json
import re

class UolConfereSpider(scrapy.Spider):
    name = "uol_confere"
    allowed_domains = ["noticias.uol.com.br"]
    start_urls = ["https://noticias.uol.com.br/confere/"]

    # Contador de notícias
    count = 0
    max_count = 200  # Limite de notícias

    def parse(self, response):
        # Verifica se o limite foi atingido
        if self.count >= self.max_count:
            return

        for manchete in response.css('.thumbnails-wrapper a'):
            link = manchete.css('::attr(href)').get()

            # Incrementa o contador e verifica o limite
            if self.count < self.max_count:
                self.count += 1
                yield response.follow(link, self.parse_article)
            else:
                return  # Para de coletar mais notícias se atingir o limite

        # Pega a próxima página via AJAX se o limite não foi atingido
        next_page = response.css('button.ver-mais::attr(data-request)').get()
        if next_page is not None and self.count < self.max_count:
            next_data = json.loads(next_page)
            next_url = self.get_next_url(next_data)

            if next_url:
                yield scrapy.Request(url=next_url, callback=self.parse_ajax)

    def parse_article(self, response):
        dados = {
            'link': response.url,
            'title': response.css('.title-content h1::text').get(),
            'author': response.css('.solar-author-name::text').get(),
            'data': response.css('.solar-author-date div time::text').get(),
            'text': re.sub(r'<.*?>', '', ' '.join(response.css('.jupiter-paragraph-fragment strong,p::text').getall())),
        }

        yield dados

    def parse_ajax(self, response):
        # Verifica se o limite foi atingido
        if self.count >= self.max_count:
            return

        for manchete in response.css('.thumbnails-wrapper a'):
            link = manchete.css('::attr(href)').get()

            # Incrementa o contador e verifica o limite
            if self.count < self.max_count:
                self.count += 1
                yield response.follow(link, self.parse_article)
            else:
                return  # Para de coletar mais notícias se atingir o limite

        # Pega a próxima página via AJAX se o limite não foi atingido
        next_page = response.css('button.ver-mais::attr(data-request)').get()
        if next_page is not None and self.count < self.max_count:
            next_data = json.loads(next_page)
            next_url = self.get_next_url(next_data)

            if next_url:
                yield scrapy.Request(url=next_url, callback=self.parse_ajax)

    def get_next_url(self, next_data):
        next_params = next_data.get('busca', {}).get('params', {})
        next_token = next_params.get('next')
        if next_token:
            return f"https://noticias.uol.com.br/confere/?next={next_token}"
        return None
