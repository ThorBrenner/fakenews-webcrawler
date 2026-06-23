import scrapy


class NewsItem(scrapy.Item):
    """Item padronizado para notícias/checagens de todas as agências.

    Nem todos os campos são preenchidos por todas as agências; os ausentes
    ficam vazios e são gravados como NULL no banco.
    """

    link = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    data = scrapy.Field()      # data publicada (texto bruto extraído do site)
    text = scrapy.Field()
    tag = scrapy.Field()
    fact = scrapy.Field()      # afirmação verificada (aosfatos)
    check = scrapy.Field()     # veredito/checagem (aosfatos)
    subject = scrapy.Field()   # assunto (lupa)
