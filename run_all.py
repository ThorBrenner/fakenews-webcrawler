"""Executa todos os spiders das agências de fact-checking em sequência.

Como agora é um único projeto Scrapy, basta rodar `scrapy crawl <spider>`
a partir da raiz. Falhas em um spider não interrompem os demais.
"""

import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SPIDERS = [
    "g1_fato_ou_fake",
    "g1_fato_ou_fake_eleicoes",
    "uol_confere",
    "lupa",
    "boatos",
    "aosfatos",
]


def run_spider(spider: str) -> int:
    cmd = ["scrapy", "crawl", spider]

    # Limite opcional de itens por spider (útil para testes rápidos).
    item_limit = os.getenv("CLOSESPIDER_ITEMCOUNT")
    if item_limit:
        cmd += ["-s", f"CLOSESPIDER_ITEMCOUNT={item_limit}"]

    print(f"[run_all] >>> {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=BASE_DIR)
    print(f"[run_all] <<< {spider} finalizado (exit={result.returncode})", flush=True)
    return result.returncode


def main() -> int:
    failures = 0
    for spider in SPIDERS:
        try:
            if run_spider(spider) != 0:
                failures += 1
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"[run_all] ERRO em {spider}: {exc}", flush=True)
    print(f"[run_all] concluído. Falhas: {failures}", flush=True)
    return failures


if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 1)
