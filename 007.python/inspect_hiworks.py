import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:8080")

try:
    driver = webdriver.Chrome(options=options)
    print("[Success] Connected to Chrome!")
except Exception as e:
    print(f"[Error] Failed to connect to Chrome on port 8080: {e}")
    sys.exit(1)

# Find the active hiworks write window/tab
hiworks_handle = None
original_handle = driver.current_window_handle

for handle in driver.window_handles:
    driver.switch_to.window(handle)
    if "mails.office.hiworks.com/write" in driver.current_url or "hiworks.com/write" in driver.current_url:
        hiworks_handle = handle
        break

if not hiworks_handle:
    print("[Error] Active Hiworks write tab not found! Please make sure a Hiworks Mail Write tab is open in Chrome 8080.")
    sys.exit(1)

print(f"[Success] Found Hiworks write tab: {driver.current_url}")

# Let's inspect the page
output_path = os.path.join(os.path.dirname(__file__), "inspect_hiworks_output.txt")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(f"URL: {driver.current_url}\n\n")
    
    # 1. Inspect all input elements
    f.write("=== INPUTS ===\n")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    for i, inp in enumerate(inputs):
        try:
            f.write(f"{i}: tag=input, id={inp.get_attribute('id')}, name={inp.get_attribute('name')}, class={inp.get_attribute('class')}, placeholder={inp.get_attribute('placeholder')}\n")
        except Exception as e:
            f.write(f"{i}: error={e}\n")
            
    # 2. Inspect all textarea elements
    f.write("\n=== TEXTAREAS ===\n")
    textareas = driver.find_elements(By.TAG_NAME, "textarea")
    for i, ta in enumerate(textareas):
        try:
            f.write(f"{i}: tag=textarea, id={ta.get_attribute('id')}, name={ta.get_attribute('name')}, class={ta.get_attribute('class')}, placeholder={ta.get_attribute('placeholder')}\n")
        except Exception as e:
            f.write(f"{i}: error={e}\n")

    # 3. Inspect all iframes
    f.write("\n=== IFRAMES ===\n")
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for i, iframe in enumerate(iframes):
        try:
            f.write(f"{i}: tag=iframe, id={iframe.get_attribute('id')}, name={iframe.get_attribute('name')}, title={iframe.get_attribute('title')}, class={iframe.get_attribute('class')}\n")
        except Exception as e:
            f.write(f"{i}: error={e}\n")

    # 4. Search for placeholder or text containing "받는사람", "제목", "수신"
    f.write("\n=== TEXT/PLACEHOLDER SEARCH ===\n")
    elements = driver.find_elements(By.XPATH, "//*[contains(text(), '받는사람') or contains(text(), '제목') or contains(text(), '참조') or contains(text(), '수신')]")
    for i, el in enumerate(elements):
        try:
            if el.text.strip():
                f.write(f"{i}: tag={el.tag_name}, class={el.get_attribute('class')}, text={el.text.strip()[:60]}\n")
        except Exception as e:
            pass

print(f"[Success] Saved inspection results to {output_path}!")
driver.switch_to.window(original_handle)
