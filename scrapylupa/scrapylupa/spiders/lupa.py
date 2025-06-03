import scrapy
from scrapy.utils.log import configure_logging

class LupaSpider(scrapy.Spider):
    name = 'lupa'

    configure_logging(install_root_handler=False)

    def start_requests(self):
        url = 'https://lupa.uol.com.br/jornalismo/categoria/checagem'
        yield scrapy.Request(
            url,
            self.parse,
            meta={
                "playwright": True,
                "playwright_page_coroutines": [
                    {"method": "click", "selector": "button.sc-cabOPr.bGDmDu", "delay": 6000},
                    {"method": "wait_for_selector", "selector": "a.sc-eDWCr.hNENvd"},
                ]
            }
        )

    async def parse(self, response):
        for manchete in response.css('a.sc-eDWCr.hNENvd'):
            link = manchete.css('::attr(href)').get()

            if link:
                full_link = response.urljoin(link)
                yield response.follow(full_link, self.parse_article, meta={"playwright": True, "playwright_page_coroutines": [{"method": "wait_for_selector", "selector": ".sc-jSUZER.eLXOCB"},]})

    async def parse_article(self, response):
        dados = {
            'link': response.url,
            'title': response.css('.sc-eDvSVe.hsxZzW::text').get(),
            'data': response.css('.sc-eDvSVe.fJkPUE::text').get(),
            'author': ' , '.join(response.css('.sc-csuSiG.kmJMjO::text').getall()),
            'text': ' '.join(response.css('.sc-jSUZER.eLXOCB::text').getall()),
            'tag': ' - '.join(response.css('.sc-eDvSVe.bMMjGB::text').getall()[1:]),
            'subject': response.css('.sc-eDvSVe.bMMjGB::text').get()
        }

        yield dados
