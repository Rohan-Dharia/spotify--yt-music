from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

options = Options()
# Path to the Chrome User Data directory
user_data_dir = "/home/rohan/.config/google-chrome"
# Name of the profile directory
profile_directory = "Profile 2"

options.add_argument(f"--user-data-dir={user_data_dir}")
options.add_argument(f"--profile-directory={profile_directory}")
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")  # 👈 Helps with Chrome profile reuse
options.add_argument("--disable-features=ChromeWhatsNewUI") 

# Start Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
try:
    driver.get("https://music.youtube.com/")
    print("page laoded")
except Exception as e:
    print("not loaded {e}")    
time.sleep(500)
# Perform your automation tasks here
# driver.quit()  # Uncomment this line when you want to close the browser