from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

# Configuration
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_DRIVER_PATH = r"C:\Users\rohan\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
USER_DATA_DIR = r"C:\Users\rohan\AppData\Local\Google\Chrome\User Data"
PROFILE_DIR = "Default"
LIKED_SONGS_URL = "https://music.youtube.com/playlist?list=LM"
SCROLL_PASSES = 5  # Number of times to scroll to load all songs
SCROLL_DELAY = 2  # Seconds to wait between scrolls
ACTION_DELAY = 1.5  # Seconds to wait between actions

def setup_driver():
    """Configure and return Chrome WebDriver"""
    options = Options()
    options.binary_location = CHROME_PATH
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    options.add_argument(f"--profile-directory={PROFILE_DIR}")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    print("🔧 Starting Chrome driver...")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def load_all_songs(driver):
    """Scroll to load all songs in the playlist"""
    print("📜 Scrolling to load all songs...")
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    
    for i in range(SCROLL_PASSES):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(SCROLL_DELAY)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print(f"   🔁 Scroll pass {i + 1} - New height: {new_height}px")

def remove_songs(driver):
    """Remove all songs from the liked playlist"""
    songs = driver.find_elements(By.CSS_SELECTOR, "ytmusic-responsive-list-item-renderer")
    print(f"🎯 Found {len(songs)} songs to remove.")
    
    actions = ActionChains(driver)
    
    for i, song in enumerate(songs, 1):
        try:
            print(f"\n➡️  Processing song {i}/{len(songs)}...")
            
            # Scroll the song into view first
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", song)
            time.sleep(1)
            
            # Hover and click the menu button
            actions.move_to_element(song).perform()
            time.sleep(1.5)
            
            # Find and click the menu button (three dots)
            menu_button = WebDriverWait(song, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "ytmusic-menu-renderer"))
            )
            driver.execute_script("arguments[0].click();", menu_button)
            print("   🎯 Opened song menu")
            
            # Wait for menu to appear - using more specific selector
            try:
                menu = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ytmusic-menu-popup-renderer tp-yt-paper-listbox"))
                )
            except:
                # Fallback if the first selector fails
                menu = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tp-yt-paper-listbox"))
                )
            
            # Find all menu items
            menu_items = menu.find_elements(By.CSS_SELECTOR, "ytmusic-menu-service-item-renderer")
            
            # Click the remove option
            for item in menu_items:
                if "remove from playlist" in item.text.lower():
                    driver.execute_script("arguments[0].click();", item)
                    print("   🗑️  Removed from playlist")
                    time.sleep(1.5)
                    break
            
        except Exception as e:
            print(f"   ❌ Error on song {i}: {str(e)[:100]}...")
            continue

def main():
    driver = setup_driver()
    
    try:
        # Open YouTube Music liked playlist
        print("🎵 Opening Liked Songs playlist...")
        driver.get(LIKED_SONGS_URL)
        time.sleep(5)  # Wait for initial load
        
        # Load all songs by scrolling
        load_all_songs(driver)
        
        # Remove all songs
        remove_songs(driver)
        
        print("\n✅ Finished removing songs from the playlist.")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    main()