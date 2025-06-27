# Selectors for Twitter/X post box and post/tweet button
POST_BOX_SELECTORS = [
    'div[aria-label="Tweet text"]',
    'div[aria-label="Post text"]',
    'div[aria-label="What\'s happening?"]',
    'div[data-testid="tweetTextarea_0"]',
    'div[data-testid="tweetTextarea_1"]',
    'div[role="textbox"]',
]

POST_BUTTON_SELECTORS = [
    '//button[@data-testid="tweetButtonInline"]',
    '//div[@data-testid="tweetButtonInline"]',
    '//div[@data-testid="tweetButton"]',
    '//div[@data-testid="tweetButtonButton"]',
    '//div[@role="button" and .//span[text()="Post"]]',
    '//div[@role="button" and .//span[text()="Tweet"]]',
] 