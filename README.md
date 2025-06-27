# Twitter/X Selenium Automation Toolkit

## Features
- Post to Twitter/X via browser automation (Selenium)
- Like, retweet, follow, and reply to tweets by hashtag/search or tweet URL
- Retweet and follow users in one go
- Follow users who retweeted a tweet (with max limit and random delay)
- Robust error handling, screenshots, and logging
- Beautiful color output with [rich](https://github.com/Textualize/rich) (optional)
- Interactive menu-driven interface with [questionary](https://github.com/tmbo/questionary)

## Why Selenium Only?
Due to Twitter/X API restrictions, most automation is only possible via browser automation. This project uses Selenium to simulate a real user for posting tweets and can be extended for other actions.

## Setup
1. `pip install -r requirements.txt`
2. For Selenium: Chrome must be installed.
3. (Required for menu) Install questionary: `pip install questionary`
4. (Optional) For beautiful CLI output, install rich: `pip install rich`

## Usage

### Interactive Menu (Recommended)

1. Make sure you have installed all requirements:
   ```sh
   pip install -r requirements.txt
   pip install questionary
   ```
2. Run the script:
   ```sh
   python twitter_selenium.py
   ```
3. Use the arrow keys to select an action:
   - Post a tweet
   - Like tweets
   - Retweet tweets
   - Follow users
   - Reply to a tweet
   - Retweet and follow users
   - Follow users who retweeted a tweet
4. Enter your username, password, and any other required info as prompted.

**Example:**
```
What do you want to do?
> Post a tweet
  Like tweets
  Retweet tweets
  Follow users
  Reply to a tweet
  Retweet and follow users
  Follow users who retweeted a tweet
```

- For 'Retweet and follow users', the bot will retweet and then follow the user for each tweet found by your search.
- For 'Follow users who retweeted a tweet', the bot will open the retweeters popup for a tweet and follow up to your specified maximum number of users, with a random delay (2–6 seconds) between follows for human-like behavior.

- Screenshots of errors are saved in `screenshots/`
- For UI changes, update selectors in `utils/selectors.py`

## Security
- Never share your credentials or screenshots containing sensitive information.
- For automation, consider using environment variables or a `.env` file for credentials (not included by default).

## .gitignore
- Add `.env`, `screenshots/`, `selenium_log.txt`, and any files with sensitive data to `.gitignore`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details. 