#

```
 ______           __________         __ 
/_  __/    _____ / __/_  __/__ ___ _/ / 
 / / | |/|/ / -_) _/  / / / -_) _ `/ /__
/_/  |__,__/\__/___/ /_/  \__/\_,_/____/
                                         
      Twitter Multi-Account Bot
```

---

> **⚠️ DYOR: Do Your Own Research!**
>
> - Use this tool responsibly and in accordance with Twitter/X terms of service.
> - Automation can carry risks, including account suspension or bans.
> - You are solely responsible for your actions and accounts.
> - Always review and understand what the tool does before using it.

---

## Safety Tips

- Mimic human behavior: use random delays, avoid mass actions.
- Warm up new accounts with manual use before automating.
- Limit automation: don't like/follow/tweet too much at once.
- Use proxies or different IPs for multiple accounts.
- Watch for captchas or verification challenges—stop if prompted.
- Stay updated: Twitter changes detection methods often.

> **No tool can guarantee your account is safe from bans. Use at your own risk.**

---

# Twitter Multi-Account Automation Bot

Automate Twitter/X with style. Manage multiple accounts, tweet in bulk, like from timeline, and more—all from a beautiful CLI.

---

## Menu Screenshot

```
==================================================
Welcome to the Twitter/X Twikit Automation Menu!
==================================================

What do you want to do?
  1. Post a tweet
  2. Schedule a tweet
  3. Tweet multiple tweets (bulk)
  4. Tweet a thread
  5. Import tweets from CSV (bulk)
  6. Import tweets from CSV (thread)
  7. Export log to CSV
  8. Like tweets
  9. Retweet tweets
 10. Follow users
 11. Reply to a tweet
 12. Retweet and follow users
 13. Follow users who retweeted a tweet
 14. Like tweets from timeline
==================================================
Select an option (1-14):
```

---

## Features

- Multi-account management
- Session persistence (auto-login)
- Bulk/thread tweeting (manual or CSV)
- Like tweets from timeline
- Schedule tweets
- Like, retweet, follow, reply (search or timeline)
- CSV import/export
- Custom/random delay between actions
- Colorful, clear CLI with ASCII art

---

## Getting Started

### Windows
1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/windows/)
2. Open Command Prompt and run:
   ```sh
   pip install twikit rich
   python twitter_twikit.py
   ```

### Mac
1. Install Python 3.10+ (recommended: [Homebrew](https://brew.sh/))
   ```sh
   brew install python
   ```
2. Open Terminal and run:
   ```sh
   pip3 install twikit rich
   python3 twitter_twikit.py
   ```

### Linux
1. Install Python 3.10+ (use your distro's package manager)
   ```sh
   sudo apt update && sudo apt install python3 python3-pip   # Debian/Ubuntu
   # or
   sudo dnf install python3 python3-pip                      # Fedora
   ```
2. Open Terminal and run:
   ```sh
   pip3 install twikit rich
   python3 twitter_twikit.py
   ```

---

## Usage

- Manage accounts (add/remove/list)
- Select one or more accounts
- Choose an action:
  - Post, schedule, bulk/thread tweet
  - Like/retweet/follow/reply (search or timeline)
  - Import/export CSV
- Enter delay (or leave blank for random)
- Return to menu or exit

---

## CSV Format
- **Import**: One tweet per line, no header
- **Export**: Log CSV with timestamp/message

---

## License
MIT

---

## Contributing & Contact

- Want to follow, contribute, or make suggestions?
- Open a pull request, or contact [@rickyzakariap](https://twitter.com/rickyzakariap)
- Feedback and ideas are welcome!

---

Built with [Twikit](https://github.com/d60/twikit) and [rich](https://github.com/Textualize/rich) 