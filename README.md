# fakenews-webcrawling

Este projeto tem como objetivo aprender e demonstrar técnicas de raspagem de dados na web (web crawling) utilizando o framework [Scrapy](https://scrapy.org/) em Python. O foco está na coleta de notícias verificadas por agências de fact-checking brasileiras, como Aos Fatos, Lupa, Boatos.org, G1 Fato ou Fake, entre outras.

## Estrutura do Projeto

O repositório está organizado em subpastas, cada uma contendo um projeto Scrapy dedicado a uma agência de checagem de fatos:

- `scrapyaosfatos/`
- `scrapylupa/`
- `scrapyboatos/`
- `scrapyg1/`
- `scrapyuol/`

Cada subpasta contém seus próprios spiders, configurações e arquivos de saída (JSON).

## Como Utilizar

1. **Pré-requisitos**  
   - Python 3.8+
   - Instale as dependências com:
     ```sh
     pip install scrapy
     ```

2. **Executando um Spider**  
   Entre na pasta do projeto desejado (por exemplo, `scrapyaosfatos`) e execute:
   ```sh
   scrapy crawl <nome_do_spider> -O saida.json
   ```
   Exemplo para o spider do Aos Fatos:
   ```sh
   cd scrapyaosfatos
   scrapy crawl aosfatos -O aosfatos.json
   ```

3. **Saída**  
   Os dados coletados serão salvos em arquivos `.json` na raiz de cada projeto.

## Observações Importantes

- **Manutenção dos Spiders:**  
  Os spiders são desenvolvidos para funcionar com a estrutura atual dos sites-alvo. Qualquer alteração no layout, classes CSS ou estrutura das páginas pode fazer com que o crawler pare de funcionar corretamente. Caso isso aconteça, será necessário atualizar o código do spider correspondente.

- **Uso Educacional:**  
  Este projeto é para fins de aprendizado e pesquisa. Respeite sempre os termos de uso dos sites e as leis de proteção de dados.
---
