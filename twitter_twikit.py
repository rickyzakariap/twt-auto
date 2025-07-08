import os
import sys
import asyncio
from datetime import datetime, timedelta
import time
import getpass
import random
import json
import csv
from twikit import Client

# Optional: rich for color output
try:
    from rich.console import Console
    console = Console()
    def cprint(msg, style=None):
        console.print(msg, style=style)
except ImportError:
    def cprint(msg, style=None):
        print(msg)

def log_action(msg, logfile='twikit_log.txt'):
    with open(logfile, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def safe_input(prompt):
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        cprint('\nCancelled by user. Exiting...')
        sys.exit(0)

def safe_password(prompt):
    try:
        return getpass.getpass(prompt)
    except (KeyboardInterrupt, EOFError):
        cprint('\nCancelled by user. Exiting...')
        sys.exit(0)

def numbered_menu(prompt, choices):
    cprint(f'\n[bold magenta]{MENU_SEPARATOR}[/]')
    cprint(f'[bold yellow]{prompt}[/]')
    for idx, choice in enumerate(choices, 1):
        cprint(f"  [bold green]{idx}.[/] {choice}")
    cprint(f'[bold magenta]{MENU_SEPARATOR}[/]')
    while True:
        sel = safe_input(f"Select an option (1-{len(choices)}): ")
        if sel.isdigit() and 1 <= int(sel) <= len(choices):
            return choices[int(sel)-1]
        cprint("[red]Invalid selection. Please try again.[/]")

ACCOUNTS_FILE = 'accounts.json'

ASCII_ART = r'''

 ______           __________         __ 
/_  __/    _____ / __/_  __/__ ___ _/ / 
 / / | |/|/ / -_) _/  / / / -_) _ `/ /__
/_/  |__,__/\__/___/ /_/  \__/\_,_/____/
                                        


      Twitter Multi-Account Bot
'''

MENU_SEPARATOR = "=" * 50

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    cprint(f'[bold cyan]{ASCII_ART}[/]')
    cprint(f'[bold blue]{MENU_SEPARATOR}[/]')
    cprint('[bold blue]Welcome to the Twitter/X Twikit Automation Menu![/]')
    cprint(f'[bold blue]{MENU_SEPARATOR}[/]')

# Account management helpers

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=2)

def select_accounts_menu(accounts):
    if not accounts:
        cprint('[red]No accounts saved. Please add an account first.[/]')
        return []
    cprint('Select account(s) to use:')
    for idx, acc in enumerate(accounts, 1):
        cprint(f"  {idx}. {acc['name']} ({acc['username']})")
    cprint(f"  {len(accounts)+1}. All accounts")
    sel = safe_input(f"Enter number(s) separated by comma (e.g. 1,2) or {len(accounts)+1} for all: ")
    if sel.strip() == str(len(accounts)+1):
        return accounts
    selected = []
    for s in sel.split(','):
        s = s.strip()
        if s.isdigit() and 1 <= int(s) <= len(accounts):
            selected.append(accounts[int(s)-1])
    return selected

def add_account_menu(accounts):
    name = safe_input("Account name (for your reference): ")
    username = safe_input("Twitter username: ")
    email = safe_input("Twitter email: ")
    password = safe_password("Twitter password: ")
    cookies_file = f"cookies_{username}.json"
    accounts.append({
        'name': name,
        'username': username,
        'email': email,
        'password': password,
        'cookies_file': cookies_file
    })
    save_accounts(accounts)
    cprint(f'[green]Account {name} added![/]')

def remove_account_menu(accounts):
    if not accounts:
        cprint('[red]No accounts to remove.[/]')
        return
    cprint('Select account to remove:')
    for idx, acc in enumerate(accounts, 1):
        cprint(f"  {idx}. {acc['name']} ({acc['username']})")
    sel = safe_input(f"Enter number to remove (1-{len(accounts)}): ")
    if sel.isdigit() and 1 <= int(sel) <= len(accounts):
        acc = accounts.pop(int(sel)-1)
        save_accounts(accounts)
        cprint(f'[yellow]Account {acc["name"]} removed.[/]')
    else:
        cprint('[red]Invalid selection.[/]')

def account_management_menu():
    accounts = load_accounts()
    while True:
        print_banner()
        cprint('[bold blue]Account Management Menu[/]')
        choice = numbered_menu("Choose:", ["List accounts", "Add account", "Remove account", "Continue to actions"])
        if choice == "List accounts":
            if not accounts:
                cprint('[yellow]No accounts saved.[/]')
            else:
                for idx, acc in enumerate(accounts, 1):
                    cprint(f"  {idx}. {acc['name']} ({acc['username']})")
            safe_input("Press Enter to continue...")
        elif choice == "Add account":
            add_account_menu(accounts)
            safe_input("Press Enter to continue...")
        elif choice == "Remove account":
            remove_account_menu(accounts)
            safe_input("Press Enter to continue...")
        elif choice == "Continue to actions":
            break
        accounts = load_accounts()  # reload in case of changes
    return accounts

def collect_user_input():
    print_banner()
    menu_choices = [
        "Post a tweet",
        "Schedule a tweet",
        "Tweet multiple tweets (bulk)",
        "Tweet a thread",
        "Import tweets from CSV (bulk)",
        "Import tweets from CSV (thread)",
        "Export log to CSV",
        "Like tweets",
        "Retweet tweets",
        "Follow users",
        "Reply to a tweet",
        "Retweet and follow users",
        "Follow users who retweeted a tweet",
        "Like tweets from timeline"
    ]
    action = numbered_menu("What do you want to do?", menu_choices)
    return {'action': action}

def get_delay_input():
    delay_input = safe_input("Enter delay in seconds between actions (e.g. 180), or leave blank for random (120–240s): ")
    if delay_input.strip() == '':
        return None  # Use random
    try:
        delay = int(delay_input)
        if delay < 0:
            raise ValueError
        return delay
    except ValueError:
        cprint("[red]Invalid input. Using random delay (120–240s).[/]")
        return None

async def login_twikit(client, account):
    # Ask user if they want to use session or input new login
    cprint(f"[bold yellow]Login options for {account['name']} ({account['username']}):[/]")
    login_method = numbered_menu(
        "Choose login method:",
        ["Use saved session (cookies)", "Input new login (username & password)"]
    )
    cookies_file = account.get('cookies_file')
    username = account['username']
    if login_method == "Use saved session (cookies)":
        email = account.get('email', '')
        password = account.get('password', '')
    else:
        username = safe_input("Enter your Twitter username: ")
        password = safe_password("Enter your Twitter password: ")
        email = None  # Not used for new login
        # Update account info with new credentials
        account['username'] = username
        account['password'] = password
        # Optionally, clear email if present
        if 'email' in account:
            del account['email']
        # Save updated credentials
        accounts = load_accounts()
        for acc in accounts:
            if acc['name'] == account['name']:
                acc['username'] = username
                acc['password'] = password
                acc['cookies_file'] = cookies_file
        save_accounts(accounts)
    try:
        await client.login(
            auth_info_1=username,
            auth_info_2=email if email else username,
            password=password,
            cookies_file=cookies_file
        )
        cprint(f'[green]Login successful for {username}![/]')
        log_action(f'Login successful for {username}')
    except Exception as e:
        cprint(f'[red]Login failed for {username}: {e}[/]')
        log_action(f'Login failed for {username}: {e}')
        sys.exit(1)

async def post_tweet_twikit(client, tweet_content):
    try:
        await client.create_tweet(text=tweet_content)
        cprint('[bold green]Tweet posted successfully![/]')
        log_action('Tweet posted')
    except Exception as e:
        cprint(f'[red]Failed to post tweet: {e}[/]')
        log_action(f'Failed to post tweet: {e}')

async def schedule_tweet_twikit(client, tweet_content, schedule_time):
    try:
        # Parse schedule_time string
        dt = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
        now = datetime.now()
        wait_seconds = (dt - now).total_seconds()
        if wait_seconds > 0:
            cprint(f'[yellow]Waiting until {dt} to post tweet...[/]')
            time.sleep(wait_seconds)
        await client.create_tweet(text=tweet_content)
        cprint('[bold green]Scheduled tweet posted successfully![/]')
        log_action(f'Scheduled tweet posted at {dt}')
    except Exception as e:
        cprint(f'[red]Failed to schedule tweet: {e}[/]')
        log_action(f'Failed to schedule tweet: {e}')

async def bulk_tweets_twikit(client, tweet_list, delay=None):
    posted = 0
    for idx, tweet_content in enumerate(tweet_list, 1):
        try:
            await client.create_tweet(text=tweet_content)
            cprint(f'[green]Tweet #{idx} posted![/]')
            log_action(f'Bulk tweet #{idx} posted')
            posted += 1
        except Exception as e:
            cprint(f'[yellow]Could not post tweet #{idx}: {e}[/]')
        if idx < len(tweet_list):
            d = delay if delay is not None else random.uniform(120, 240)
            cprint(f'[yellow]Waiting {int(d)} seconds before next tweet...[/]')
            time.sleep(d)
    cprint(f'[bold green]Posted {posted} tweets in bulk.[/]')

async def thread_tweets_twikit(client, tweet_list, delay=None):
    posted = 0
    last_tweet_id = None
    for idx, tweet_content in enumerate(tweet_list, 1):
        try:
            if last_tweet_id:
                tweet = await client.reply_tweet(text=tweet_content, tweet_id=last_tweet_id)
            else:
                tweet = await client.create_tweet(text=tweet_content)
            last_tweet_id = tweet.id
            cprint(f'[green]Thread tweet #{idx} posted![/]')
            log_action(f'Thread tweet #{idx} posted')
            posted += 1
        except Exception as e:
            cprint(f'[yellow]Could not post thread tweet #{idx}: {e}[/]')
        if idx < len(tweet_list):
            d = delay if delay is not None else random.uniform(120, 240)
            cprint(f'[yellow]Waiting {int(d)} seconds before next tweet in thread...[/]')
            time.sleep(d)
    cprint(f'[bold green]Posted {posted} tweets as a thread.[/]')

async def search_tweets_twikit(client, query, count=1):
    try:
        tweets = await client.search_tweet(query, 'Latest')
        tweets = list(tweets)[:count]
        for idx, tweet in enumerate(tweets, 1):
            cprint(f"[blue]Tweet #{idx} by {tweet.user.name}: {tweet.text}[/]")
        return tweets
    except Exception as e:
        cprint(f'[red]Failed to search tweets: {e}[/]')
        log_action(f'Failed to search tweets: {e}')
        return []

async def like_tweets_twikit(client, query, count=1, delay=None):
    tweets = await search_tweets_twikit(client, query, count)
    liked = 0
    for idx, tweet in enumerate(tweets, 1):
        try:
            await client.favorite_tweet(tweet.id)
            cprint(f'[green]Liked tweet by {tweet.user.name}![/]')
            log_action(f'Liked tweet {tweet.id}')
            liked += 1
        except Exception as e:
            cprint(f'[yellow]Could not like tweet: {e}[/]')
        if idx < len(tweets):
            d = delay if delay is not None else random.uniform(120, 240)
            cprint(f'[yellow]Waiting {int(d)} seconds before next like...[/]')
            time.sleep(d)
    cprint(f'[bold green]Liked {liked} tweets.[/]')

async def retweet_tweets_twikit(client, query, count=1, delay=None):
    tweets = await search_tweets_twikit(client, query, count)
    retweeted = 0
    for idx, tweet in enumerate(tweets, 1):
        try:
            await client.retweet(tweet.id)
            cprint(f'[green]Retweeted tweet by {tweet.user.name}![/]')
            log_action(f'Retweeted tweet {tweet.id}')
            retweeted += 1
        except Exception as e:
            cprint(f'[yellow]Could not retweet: {e}[/]')
        if idx < len(tweets):
            d = delay if delay is not None else random.uniform(120, 240)
            cprint(f'[yellow]Waiting {int(d)} seconds before next retweet...[/]')
            time.sleep(d)
    cprint(f'[bold green]Retweeted {retweeted} tweets.[/]')

async def follow_users_twikit(client, query, count=1, delay=None):
    tweets = await search_tweets_twikit(client, query, count)
    followed = 0
    for idx, tweet in enumerate(tweets, 1):
        try:
            await client.follow_user(tweet.user.id)
            cprint(f'[green]Followed user {tweet.user.name}![/]')
            log_action(f'Followed user {tweet.user.id}')
            followed += 1
        except Exception as e:
            cprint(f'[yellow]Could not follow user: {e}[/]')
        if idx < len(tweets):
            d = delay if delay is not None else random.uniform(120, 240)
            cprint(f'[yellow]Waiting {int(d)} seconds before next follow...[/]')
            time.sleep(d)
    cprint(f'[bold green]Followed {followed} users.[/]')

async def reply_to_tweet_twikit(client, query, reply_text, count=1, delay=None):
    tweets = await search_tweets_twikit(client, query, count)
    replied = 0
    for idx, tweet in enumerate(tweets, 1):
        try:
            await client.create_tweet(text=reply_text, reply_to=tweet.id)
            cprint(f'[green]Replied to tweet by {tweet.user.name}![/]')
            log_action(f'Replied to tweet {tweet.id}')
            replied += 1
        except Exception as e:
            cprint(f'[yellow]Could not reply: {e}[/]')
        if idx < len(tweets):
            d = delay if delay is not None else random.uniform(120, 240)
            cprint(f'[yellow]Waiting {int(d)} seconds before next reply...[/]')
            time.sleep(d)
    cprint(f'[bold green]Replied to {replied} tweets.[/]')

async def reply_to_tweet_url_twikit(client, tweet_url, reply_text):
    try:
        tweet_id = tweet_url.rstrip('/').split('/')[-1]
        await client.create_tweet(text=reply_text, reply_to=tweet_id)
        cprint(f'[green]Replied to the tweet![/]')
        log_action(f'Replied to tweet by URL {tweet_id}')
    except Exception as e:
        cprint(f'[yellow]Could not reply to tweet: {e}[/]')
        log_action(f'Failed to reply to tweet by URL: {e}')

async def retweet_and_follow_twikit(client, query, count=1, delay=None):
    tweets = await search_tweets_twikit(client, query, count)
    interacted = 0
    for idx, tweet in enumerate(tweets, 1):
        try:
            await client.retweet(tweet.id)
            await client.follow_user(tweet.user.id)
            cprint(f'[green]Retweeted and followed {tweet.user.name}![/]')
            log_action(f'Retweeted and followed {tweet.user.id}')
            interacted += 1
        except Exception as e:
            cprint(f'[yellow]Could not retweet and follow: {e}[/]')
        if idx < len(tweets):
            d = delay if delay is not None else random.uniform(120, 240)
            cprint(f'[yellow]Waiting {int(d)} seconds before next retweet/follow...[/]')
            time.sleep(d)
    cprint(f'[bold green]Retweeted and followed {interacted} users.[/]')

async def follow_retweeters_twikit(client, tweet_url, max_users=10, delay=None):
    try:
        tweet_id = tweet_url.rstrip('/').split('/')[-1]
        users = await client.get_retweeters(tweet_id)
        followed = 0
        for idx, user in enumerate(users, 1):
            if followed >= max_users:
                break
            try:
                await client.follow_user(user.id)
                cprint(f'[green]Followed retweeter {user.name}![/]')
                log_action(f'Followed retweeter {user.id}')
                followed += 1
            except Exception as e:
                cprint(f'[yellow]Could not follow retweeter: {e}[/]')
            if idx < len(users):
                d = delay if delay is not None else random.uniform(120, 240)
                cprint(f'[yellow]Waiting {int(d)} seconds before next follow...[/]')
                time.sleep(d)
        cprint(f'[bold green]Followed {followed} retweeters.[/]')
    except Exception as e:
        cprint(f'[red]Could not get retweeters: {e}[/]')
        log_action(f'Failed to get retweeters: {e}')

async def like_timeline_twikit(client, count=1, delay=None):
    try:
        tweets = await client.get_latest_timeline(count=count)
        tweets = list(tweets)[:count]
        liked = 0
        for idx, tweet in enumerate(tweets, 1):
            try:
                await client.favorite_tweet(tweet.id)
                cprint(f'[green]Liked timeline tweet by {tweet.user.name}![/]')
                log_action(f'Liked timeline tweet {tweet.id}')
                liked += 1
            except Exception as e:
                cprint(f'[yellow]Could not like timeline tweet: {e}[/]')
            if idx < len(tweets):
                d = delay if delay is not None else random.uniform(120, 240)
                cprint(f'[yellow]Waiting {int(d)} seconds before next like...[/]')
                time.sleep(d)
        cprint(f'[bold green]Liked {liked} timeline tweets.[/]')
    except Exception as e:
        cprint(f'[red]Failed to fetch or like timeline tweets: {e}[/]')
        log_action(f'Failed to like timeline tweets: {e}')

# CSV helpers

def import_tweets_from_csv():
    path = safe_input("Enter CSV file path (one tweet per line): ")
    tweets = []
    try:
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0].strip():
                    tweets.append(row[0].strip())
        cprint(f'[green]Imported {len(tweets)} tweets from {path}.[/]')
    except Exception as e:
        cprint(f'[red]Failed to import CSV: {e}[/]')
    return tweets

def export_log_to_csv(logfile='twikit_log.txt', exportfile='twikit_log_export.csv'):
    try:
        with open(logfile, 'r', encoding='utf-8') as fin, open(exportfile, 'w', newline='', encoding='utf-8') as fout:
            writer = csv.writer(fout)
            writer.writerow(['Timestamp', 'Message'])
            for line in fin:
                if line.strip():
                    if line.startswith('['):
                        ts, msg = line.split(']', 1)
                        writer.writerow([ts.strip('[]'), msg.strip()])
                    else:
                        writer.writerow(['', line.strip()])
        cprint(f'[green]Exported log to {exportfile}.[/]')
    except Exception as e:
        cprint(f'[red]Failed to export log: {e}[/]')

async def main_menu():
    accounts = account_management_menu()
    if not accounts:
        cprint('[red]No accounts available. Exiting.[/]')
        return
    selected_accounts = select_accounts_menu(accounts)
    if not selected_accounts:
        cprint('[red]No accounts selected. Exiting.[/]')
        return
    while True:
        user_input = collect_user_input()
        action = user_input['action']
        if action == "Export log to CSV":
            export_log_to_csv()
            safe_input("Press Enter to return to main menu...")
            continue
        if action == "Import tweets from CSV (bulk)":
            tweets = import_tweets_from_csv()
            for account in selected_accounts:
                print_banner()
                cprint(f'[bold blue]Running bulk CSV tweet for account: {account["name"]} ({account["username"]})[/]')
                client = Client('en-US')
                await login_twikit(client, account)
                delay = get_delay_input()
                await bulk_tweets_twikit(client, tweets, delay)
            again = numbered_menu("What do you want to do next?", ["Return to main menu", "Exit"])
            if again == "Exit":
                cprint('[bold yellow]Goodbye![/]')
                break
            continue
        if action == "Import tweets from CSV (thread)":
            tweets = import_tweets_from_csv()
            for account in selected_accounts:
                print_banner()
                cprint(f'[bold blue]Running thread CSV tweet for account: {account["name"]} ({account["username"]})[/]')
                client = Client('en-US')
                await login_twikit(client, account)
                delay = get_delay_input()
                await thread_tweets_twikit(client, tweets, delay)
            again = numbered_menu("What do you want to do next?", ["Return to main menu", "Exit"])
            if again == "Exit":
                cprint('[bold yellow]Goodbye![/]')
                break
            continue
        for account in selected_accounts:
            print_banner()
            cprint(f'[bold blue]Running action for account: {account["name"]} ({account["username"]})[/]')
            client = Client('en-US')
            await login_twikit(client, account)
            tweet_content = None
            tweet_list = None
            schedule_time = None
            query = None
            count = 1
            reply_text = None
            tweet_url = None
            max_users = 10
            reply_mode = None
            if action == "Post a tweet":
                tweet_content = safe_input("Enter the tweet you want to post: ")
                await post_tweet_twikit(client, tweet_content)
            elif action == "Schedule a tweet":
                tweet_content = safe_input("Enter the tweet you want to schedule: ")
                schedule_time = safe_input("Enter the date and time to post (YYYY-MM-DD HH:MM, 24h): ")
                await schedule_tweet_twikit(client, tweet_content, schedule_time)
            elif action == "Tweet multiple tweets (bulk)":
                tweet_list = []
                cprint('[cyan]Enter each tweet. Leave blank and press Enter to finish.[/]')
                while True:
                    t = safe_input(f"Tweet #{len(tweet_list)+1} (leave blank to finish): ")
                    if not t:
                        break
                    tweet_list.append(t)
                delay = get_delay_input()
                await bulk_tweets_twikit(client, tweet_list, delay)
            elif action == "Tweet a thread":
                tweet_list = []
                cprint('[cyan]Enter each tweet for the thread. Leave blank and press Enter to finish.[/]')
                while True:
                    t = safe_input(f"Thread tweet #{len(tweet_list)+1} (leave blank to finish): ")
                    if not t:
                        break
                    tweet_list.append(t)
                delay = get_delay_input()
                await thread_tweets_twikit(client, tweet_list, delay)
            elif action in ["Like tweets", "Retweet tweets", "Follow users"]:
                query = safe_input("Enter the search query or hashtag: ")
                count = safe_input("How many tweets/users to process? (default 1): ")
                count = int(count) if count.isdigit() else 1
                delay = get_delay_input()
                if action == "Like tweets":
                    await like_tweets_twikit(client, query, count, delay)
                elif action == "Retweet tweets":
                    await retweet_tweets_twikit(client, query, count, delay)
                elif action == "Follow users":
                    await follow_users_twikit(client, query, count, delay)
            elif action == "Reply to a tweet":
                reply_mode = numbered_menu("Reply by search or by tweet URL?", ["Search", "Tweet URL"])
                if reply_mode == "Tweet URL":
                    tweet_url = safe_input("Enter the tweet URL: ")
                    reply_text = safe_input("Enter your reply text: ")
                    await reply_to_tweet_url_twikit(client, tweet_url, reply_text)
                else:
                    query = safe_input("Enter the search query or hashtag: ")
                    reply_text = safe_input("Enter your reply text: ")
                    count = safe_input("How many tweets/users to process? (default 1): ")
                    count = int(count) if count.isdigit() else 1
                    delay = get_delay_input()
                    await reply_to_tweet_twikit(client, query, reply_text, count, delay)
            elif action == "Retweet and follow users":
                query = safe_input("Enter the search query or hashtag: ")
                count = safe_input("How many tweets/users to process? (default 1): ")
                count = int(count) if count.isdigit() else 1
                delay = get_delay_input()
                await retweet_and_follow_twikit(client, query, count, delay)
            elif action == "Follow users who retweeted a tweet":
                tweet_url = safe_input("Enter the tweet URL: ")
                max_users = safe_input("How many retweeters to follow? (default 10): ")
                max_users = int(max_users) if max_users.isdigit() else 10
                delay = get_delay_input()
                await follow_retweeters_twikit(client, tweet_url, max_users, delay)
            elif action == "Like tweets from timeline":
                count = safe_input("How many tweets to like from timeline? (default 1): ")
                count = int(count) if count.isdigit() else 1
                delay = get_delay_input()
                await like_timeline_twikit(client, count, delay)
        again = numbered_menu("What do you want to do next?", ["Return to main menu", "Exit"])
        if again == "Exit":
            cprint('[bold yellow]Goodbye![/]')
            break

if __name__ == '__main__':
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print('\nCancelled by user. Exiting cleanly.')
        exit(0) 