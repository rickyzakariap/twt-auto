import os
import sys
import time
import random
from datetime import datetime
import questionary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.selectors import POST_BOX_SELECTORS, POST_BUTTON_SELECTORS

# Optional: rich for color output
try:
    from rich.console import Console
    console = Console()
    def cprint(msg, style=None):
        console.print(msg, style=style)
except ImportError:
    def cprint(msg, style=None):
        print(msg)

def log_action(msg, logfile='selenium_log.txt'):
    with open(logfile, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def take_screenshot(driver, prefix):
    os.makedirs('screenshots', exist_ok=True)
    path = os.path.join('screenshots', f'{prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    driver.save_screenshot(path)
    cprint(f'[yellow]Screenshot saved as {path}[/]')
    log_action(f'Screenshot: {path}')
    return path

def wait_for_element(driver, by, value, timeout=20):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))

def safe_ask(prompt_func, *args, **kwargs):
    try:
        return prompt_func(*args, **kwargs).ask()
    except (KeyboardInterrupt, EOFError):
        cprint('[yellow]Cancelled by user. Exiting...[/]')
        sys.exit(0)

def login(driver, username, password):
    cprint('[bold cyan]Opening Twitter login page...[/]')
    driver.get('https://twitter.com/login')
    time.sleep(8)
    cprint('[cyan]Entering username...[/]')
    username_input = wait_for_element(driver, By.NAME, 'text')
    username_input.send_keys(username)
    username_input.send_keys(Keys.RETURN)
    time.sleep(5)
    cprint('[cyan]Entering password...[/]')
    password_input = wait_for_element(driver, By.NAME, 'password')
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(8)
    cprint('[green]Login complete![/]')
    log_action('Login successful')

def find_post_box(driver):
    cprint('[cyan]Navigating to home timeline...[/]')
    driver.get('https://twitter.com/home')
    time.sleep(5)
    wait = WebDriverWait(driver, 20)
    for selector in POST_BOX_SELECTORS:
        try:
            post_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
            cprint(f'[green]Found post box with selector: {selector}[/]')
            return post_box
        except Exception:
            continue
    cprint('[yellow]Post box not found by direct selector. Trying to click a "Post" or "What\'s happening?" button...[/]')
    try:
        whats_happening_btn = driver.find_element(By.XPATH, "//span[contains(text(), \"What's happening?\")]")
        whats_happening_btn.click()
        cprint('[green]Clicked "What\'s happening?" button.[/]')
        time.sleep(2)
    except Exception:
        try:
            post_btn = driver.find_element(By.XPATH, "//a[@aria-label='Post']")
            post_btn.click()
            cprint('[green]Clicked "Post" button.[/]')
            time.sleep(2)
        except Exception:
            cprint('[red]Could not find a button to open the post composer.[/]')
    for selector in POST_BOX_SELECTORS:
        try:
            post_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
            cprint(f'[green]Found post box with selector: {selector} after clicking button.[/]')
            return post_box
        except Exception:
            continue
    return None

def find_post_button(driver):
    cprint('[cyan]Looking for post/tweet button...[/]')
    for bsel in POST_BUTTON_SELECTORS:
        try:
            post_button = driver.find_element(By.XPATH, bsel)
            cprint(f'[green]Found post/tweet button with selector: {bsel}[/]')
            return post_button
        except Exception:
            continue
    return None

def post_tweet(driver, tweet_content):
    post_box = find_post_box(driver)
    if not post_box:
        raise Exception('Could not find the post box. Twitter/X UI may have changed.')
    post_box.click()
    post_box.send_keys(tweet_content)
    time.sleep(4)
    post_button = find_post_button(driver)
    if not post_button:
        raise Exception('Could not find the post/tweet button. Twitter/X UI may have changed.')
    cprint(f'[yellow]Button disabled attribute: {post_button.get_attribute("disabled")}[/]')
    cprint(f'[yellow]Button class: {post_button.get_attribute("class")}[/]')
    driver.execute_script('arguments[0].scrollIntoView(true);', post_button)
    take_screenshot(driver, 'before_click')
    time.sleep(2)
    try:
        post_button.click()
        cprint('[green]Clicked post/tweet button (normal click).[/]')
    except Exception as e:
        cprint(f'[yellow]Normal click failed, trying JavaScript click: {e}[/]')
        driver.execute_script('arguments[0].click();', post_button)
        cprint('[green]Clicked post/tweet button (JavaScript click).[/]')
    cprint('[bold green]Post (tweet) sent successfully![/]')
    log_action('Tweet posted')

def search_and_interact(driver, action, query, count, reply_text=None):
    cprint(f'[cyan]Searching for tweets with query: {query}[/]')
    driver.get(f'https://twitter.com/search?q={query}&src=typed_query&f=live')
    time.sleep(5)
    # Auto-scroll untuk memuat lebih banyak tweet
    scroll_attempts = 3
    for _ in range(scroll_attempts):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
    tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    cprint(f'[cyan]Jumlah tweet ditemukan: {len(tweets)}[/]')
    if not tweets:
        cprint('[red]Tidak ada tweet ditemukan untuk query tersebut![/]')
        log_action(f'No tweets found for query: {query}')
        take_screenshot(driver, f'{action}_no_tweets')
        input('Tekan Enter untuk menutup browser...')
        return
    interacted = 0
    for idx, tweet in enumerate(tweets[:count]):
        try:
            # Screenshot tweet sebelum aksi
            driver.execute_script("arguments[0].scrollIntoView(true);", tweet)
            time.sleep(1)
            take_screenshot(driver, f'{action}_tweet_{idx+1}')
            # Print semua data-testid di tweet
            data_testids = [el.get_attribute('data-testid') for el in tweet.find_elements(By.XPATH, './/*[@data-testid]')]
            cprint(f'[blue]Tweet #{idx+1} data-testids: {data_testids}[/]')
            if action == 'like':
                # Cari SVG icon like berdasarkan class unik
                svg_like_btns = tweet.find_elements(By.XPATH, ".//svg[contains(@class, 'r-4qtqp9') and contains(@class, 'r-yyyyoo')]")
                if not svg_like_btns:
                    cprint('[yellow]Tweet ini tidak punya tombol like (mungkin sudah di-like atau bukan tweet publik).[/]')
                    continue
                svg_like = svg_like_btns[0]
                # Cari parent <div> atau <button> terdekat
                parent = svg_like
                for _ in range(4):  # Naik max 4 level
                    parent = parent.find_element(By.XPATH, './..')
                    if parent.tag_name in ['div', 'button']:
                        break
                driver.execute_script("arguments[0].scrollIntoView(true);", parent)
                time.sleep(0.5)
                parent.click()
                cprint(f'[green]Liked a tweet![/]')
                log_action(f'Liked a tweet for query: {query}')
            elif action == 'retweet':
                rt_btn = tweet.find_element(By.XPATH, './/div[@data-testid="retweet"]')
                rt_btn.click()
                time.sleep(1)
                confirm_btn = driver.find_element(By.XPATH, '//div[@data-testid="retweetConfirm"]')
                confirm_btn.click()
                cprint(f'[green]Retweeted a tweet![/]')
                log_action('Retweeted a tweet')
            elif action == 'follow':
                user_link = tweet.find_element(By.XPATH, './/a[contains(@href, "/status/")]/../../..//div[@dir="ltr"]/span')
                user_link.click()
                time.sleep(3)
                follow_btn = driver.find_element(By.XPATH, '//div[@data-testid="placementTracking"]//span[text()="Follow"]/ancestor::div[@role="button"]')
                follow_btn.click()
                cprint(f'[green]Followed a user![/]')
                log_action('Followed a user')
                driver.back()
                time.sleep(random.uniform(2, 6))
            elif action == 'reply' and reply_text:
                reply_btn = tweet.find_element(By.XPATH, './/div[@data-testid="reply"]')
                reply_btn.click()
                time.sleep(2)
                reply_box = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Tweet your reply"]')
                reply_box.send_keys(reply_text)
                time.sleep(1)
                reply_post_btn = driver.find_element(By.XPATH, '//div[@data-testid="tweetButtonInline"]')
                reply_post_btn.click()
                cprint(f'[green]Replied to a tweet![/]')
                log_action('Replied to a tweet')
                time.sleep(2)
            interacted += 1
            time.sleep(random.uniform(2, 6))
        except Exception as e:
            cprint(f'[yellow]Could not {action} tweet: {e}[/]')
            take_screenshot(driver, f'{action}_error')
    if action == 'like' and interacted > 0:
        log_action(f'Successfully liked {interacted} tweet(s) for query: {query}')
    if action == 'like' and interacted == 0:
        log_action(f'No tweets liked for query: {query}')
        cprint('[red]Tidak ada tweet yang berhasil di-like. Coba ganti query, atau cek apakah tweet sudah di-like sebelumnya.[/]')
    cprint(f'[bold green]{action.capitalize()}d {interacted} tweets.[/]')

def reply_to_tweet_url(driver, tweet_url, reply_text):
    cprint(f'[cyan]Navigating to tweet: {tweet_url}[/]')
    driver.get(tweet_url)
    time.sleep(5)
    try:
        reply_btn = driver.find_element(By.XPATH, '//div[@data-testid="reply"]')
        reply_btn.click()
        time.sleep(2)
        reply_box = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Tweet your reply"]')
        reply_box.send_keys(reply_text)
        time.sleep(1)
        reply_post_btn = driver.find_element(By.XPATH, '//div[@data-testid="tweetButtonInline"]')
        reply_post_btn.click()
        cprint(f'[green]Replied to the tweet![/]')
        log_action('Replied to a tweet by URL')
    except Exception as e:
        cprint(f'[yellow]Could not reply to tweet: {e}[/]')
        take_screenshot(driver, 'reply_url_error')

def retweet_and_follow(driver, query, count):
    cprint(f'[cyan]Searching for tweets with query: {query}[/]')
    driver.get(f'https://twitter.com/search?q={query}&src=typed_query&f=live')
    time.sleep(5)
    tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    interacted = 0
    for tweet in tweets[:count]:
        try:
            # Retweet
            rt_btn = tweet.find_element(By.XPATH, './/div[@data-testid="retweet"]')
            rt_btn.click()
            time.sleep(1)
            confirm_btn = driver.find_element(By.XPATH, '//div[@data-testid="retweetConfirm"]')
            confirm_btn.click()
            cprint(f'[green]Retweeted a tweet![/]')
            log_action('Retweeted a tweet')
            # Follow user
            user_link = tweet.find_element(By.XPATH, './/a[contains(@href, "/status/")]/../../..//div[@dir="ltr"]/span')
            user_link.click()
            time.sleep(3)
            follow_btn = driver.find_element(By.XPATH, '//div[@data-testid="placementTracking"]//span[text()="Follow"]/ancestor::div[@role="button"]')
            follow_btn.click()
            cprint(f'[green]Followed a user![/]')
            log_action('Followed a user')
            driver.back()
            time.sleep(random.uniform(2, 6))
            interacted += 1
            time.sleep(random.uniform(2, 6))
        except Exception as e:
            cprint(f'[yellow]Could not retweet and follow: {e}[/]')
            take_screenshot(driver, 'retweet_follow_error')
    cprint(f'[bold green]Retweeted and followed {interacted} users.[/]')

def follow_retweeters(driver, tweet_url, max_users=10):
    cprint(f'[cyan]Navigating to tweet: {tweet_url}[/]')
    driver.get(tweet_url)
    time.sleep(5)
    try:
        # Click the 'Retweets' count to open the popup
        retweet_count_btn = driver.find_element(By.XPATH, '//a[contains(@href, "/retweets")]')
        retweet_count_btn.click()
        cprint('[green]Opened retweeters popup.[/]')
        time.sleep(3)
        users = driver.find_elements(By.XPATH, '//div[@data-testid="UserCell"]//a[contains(@href, "/status/")]/../../..//div[@dir="ltr"]/span')
        followed = 0
        for user in users:
            if followed >= max_users:
                break
            try:
                user.click()
                time.sleep(3)
                follow_btn = driver.find_element(By.XPATH, '//div[@data-testid="placementTracking"]//span[text()="Follow"]/ancestor::div[@role="button"]')
                follow_btn.click()
                cprint(f'[green]Followed a retweeter![/]')
                log_action('Followed a retweeter')
                driver.back()
                time.sleep(random.uniform(2, 6))
                followed += 1
            except Exception as e:
                cprint(f'[yellow]Could not follow retweeter: {e}[/]')
                take_screenshot(driver, 'follow_retweeter_error')
        cprint(f'[bold green]Followed {followed} retweeters.[/]')
    except Exception as e:
        cprint(f'[red]Could not open retweeters popup or follow users: {e}[/]')
        take_screenshot(driver, 'retweeters_popup_error')

# === ENTRY POINT ===
def main():
    cprint('[bold blue]Twitter/X Selenium Automation Menu[/]')
    # === COLLECT ALL INPUT FIRST ===
    action = safe_ask(questionary.select, "What do you want to do?", choices=[
        "Post a tweet",
        "Like tweets",
        "Retweet tweets",
        "Follow users",
        "Reply to a tweet",
        "Retweet and follow users",
        "Follow users who retweeted a tweet"
    ])
    username = safe_ask(questionary.text, "Enter your Twitter username or email:")
    password = safe_ask(questionary.password, "Enter your Twitter password:")
    tweet_content = None
    query = None
    count = 1
    reply_text = None
    tweet_url = None
    max_users = 10
    if action == "Post a tweet":
        tweet_content = safe_ask(questionary.text, "Enter the tweet you want to post:")
    elif action in ["Like tweets", "Retweet tweets", "Follow users"]:
        query = safe_ask(questionary.text, "Enter the search query or hashtag:")
        count = int(safe_ask(questionary.text, "How many tweets/users to process? (default 1)") or "1")
    elif action == "Reply to a tweet":
        reply_mode = safe_ask(questionary.select, "Reply by search or by tweet URL?", choices=["Search", "Tweet URL"])
        if reply_mode == "Tweet URL":
            tweet_url = safe_ask(questionary.text, "Enter the tweet URL:")
            reply_text = safe_ask(questionary.text, "Enter your reply text:")
        else:
            query = safe_ask(questionary.text, "Enter the search query or hashtag:")
            reply_text = safe_ask(questionary.text, "Enter your reply text:")
            count = int(safe_ask(questionary.text, "How many tweets/users to process? (default 1)") or "1")
    elif action == "Retweet and follow users":
        query = safe_ask(questionary.text, "Enter the search query or hashtag:")
        count = int(safe_ask(questionary.text, "How many tweets/users to process? (default 1)") or "1")
    elif action == "Follow users who retweeted a tweet":
        tweet_url = safe_ask(questionary.text, "Enter the tweet URL:")
        max_users = int(safe_ask(questionary.text, "How many retweeters to follow? (default 10)") or "10")
    # === ONLY NOW OPEN THE BROWSER ===
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        login(driver, username, password)
        if action == "Post a tweet":
            post_tweet(driver, tweet_content)
        elif action in ["Like tweets", "Retweet tweets", "Follow users"]:
            act = action.split()[0].lower()
            search_and_interact(driver, act, query, count)
        elif action == "Reply to a tweet":
            if tweet_url and reply_text:
                reply_to_tweet_url(driver, tweet_url, reply_text)
            elif query and reply_text:
                search_and_interact(driver, "reply", query, count, reply_text)
        elif action == "Retweet and follow users":
            retweet_and_follow(driver, query, count)
        elif action == "Follow users who retweeted a tweet":
            follow_retweeters(driver, tweet_url, max_users)
    except Exception as e:
        cprint(f'[red]Failed to perform action: {e}[/]')
        log_action(f'Error: {e}')
        take_screenshot(driver, 'twitter_error')
    finally:
        time.sleep(8)
        driver.quit()

if __name__ == '__main__':
    main() 