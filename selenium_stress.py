"""
Нагрузочный сценарий через Selenium WebDriver (реальный браузер Chromium).
Несколько потоков параллельно открывают форму, отправляют её и проверяют ответ.
"""

import os
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("WEBAPP_URL", "http://webapp:5000").rstrip("/")
WORKERS = int(os.environ.get("SELENIUM_WORKERS", "4"))
ROUNDS_PER_WORKER = int(os.environ.get("SELENIUM_ROUNDS", "8"))
USER_NAME = os.environ.get("SELENIUM_USERNAME", "SeleniumUser")


def build_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,720")
    opts.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=opts)


def run_worker(worker_id: int) -> tuple[int, int]:
    ok, fail = 0, 0
    driver = build_driver()
    try:
        for r in range(ROUNDS_PER_WORKER):
            try:
                driver.get(f"{BASE_URL}/")
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                inp = driver.find_element(By.NAME, "username")
                inp.clear()
                inp.send_keys(USER_NAME)
                driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
                el = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.ID, "result"))
                )
                text = el.text or ""
                if f"Saved: {USER_NAME}" not in text:
                    raise AssertionError(f"unexpected #result: {text!r}")
                h1 = driver.find_element(By.TAG_NAME, "h1").text.strip()
                if h1 != "Stress Test Target":
                    raise AssertionError(f"unexpected h1: {h1!r}")
                ok += 1
            except Exception:
                fail += 1
                print(f"[worker {worker_id} round {r}] error:", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
    finally:
        driver.quit()
    return ok, fail


def main() -> None:
    print(
        f"Selenium stress: {WORKERS} workers * {ROUNDS_PER_WORKER} rounds - "
        f"{WORKERS * ROUNDS_PER_WORKER} UI-проходов, target {BASE_URL}",
        flush=True,
    )
    total_ok = total_fail = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(run_worker, i): i for i in range(WORKERS)}
        for fut in as_completed(futures):
            o, f = fut.result()
            total_ok += o
            total_fail += f
    print(f"Done. OK={total_ok} FAIL={total_fail}", flush=True)
    if total_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
