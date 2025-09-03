# tools/capture_screens.py
# Run while the Streamlit app is running.

import os, time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

APP_URL = os.environ.get("APP_URL", "http://localhost:8504")  # change if needed
TABS = ["Overview", "Customers", "Profiles", "EDA", "Forecasting"]

OUTDIR = Path("screenshots")
OUTDIR.mkdir(parents=True, exist_ok=True)

def open_app(url: str):
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1600,1200")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.get(url)
    return driver

def wait_for_tabbar(driver):
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'stTabs')]"))
    )

def click_tab(driver, tab_name: str):
    tab_xpath = f"//div[contains(@class,'stTabs')]//button[.='{tab_name}']"
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, tab_xpath))).click()
    time.sleep(1.2)

def save_png(driver, name: str):
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.4)
    path = OUTDIR / f"{name}.png"
    driver.save_screenshot(str(path))
    print(f"Saved {path}")

def main():
    print(f"Opening {APP_URL} ...")
    d = open_app(APP_URL)
    try:
        wait_for_tabbar(d)
        for tab in TABS:
            print(f"Capturing: {tab}")
            click_tab(d, tab)
            save_png(d, tab.lower().replace(" ", "_"))
        print("All screenshots saved in 'screenshots' folder.")
    finally:
        d.quit()

if __name__ == "__main__":
    main()