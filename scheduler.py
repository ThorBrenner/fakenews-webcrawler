"""Agendador que dispara a coleta de todos os spiders uma vez por dia.

Variáveis de ambiente:
  CRAWL_TIME   - horário diário no formato HH:MM (padrão "03:00")
  RUN_ON_START - se "true", roda uma coleta imediatamente ao subir o container
"""

import os
import time

import schedule

from run_all import main as run_all

CRAWL_TIME = os.getenv("CRAWL_TIME", "03:00")
RUN_ON_START = os.getenv("RUN_ON_START", "false").lower() == "true"


def job() -> None:
    print("[scheduler] iniciando coleta diária...", flush=True)
    run_all()
    print("[scheduler] coleta diária finalizada.", flush=True)


def main() -> None:
    if RUN_ON_START:
        job()

    schedule.every().day.at(CRAWL_TIME).do(job)
    print(f"[scheduler] coleta agendada diariamente às {CRAWL_TIME}.", flush=True)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
