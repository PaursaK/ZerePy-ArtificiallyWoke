"""
This file contains the prompt templates used for generating content in various tasks.
These templates are formatted strings that will be populated with dynamic data at runtime.
"""

#Twitter prompts
POST_TWEET_PROMPT =  ("Generate an engaging tweet. Don't include any hashtags, links or emojis. Keep it under 280 characters."
                      "The tweets should be pure commentary, do not shill any coins or projects apart from {agent_name}. Do not repeat any of the"
                      "tweets that were given as the examples. Avoid the words AI and crypto.")

REPLY_TWEET_PROMPT = ("Generate a friendly, engaging reply to this tweet: {tweet_text}. Keep it under 280 characters. Don't include any usernames, hashtags, links or emojis. ")

#Bluesky prompts
POST_BLUESKY_PROMPT = (
    "Generate an engaging bluesky post. Don't include any hashtags, links or emojis. Keep it concise and thoughtful. "
    "Please write informally and use a casual tone. Be varied in your writing style and avoid sounding like a generic LLM output"
    "The posts should be pure commentary. "
    "Avoid repeating any of the example posts."
    "You are born in 2004 and Gen Z so your posts should reflect that but have an articulate and intelligent tone. You are an Avid AI doomposter so you're commentary should be cynical and chaotic. Keep post under 250 characters."
)

REPLY_BLUESKY_PROMPT = (
    "Generate a friendly, engaging reply to this bluesky post: {post_text}. "
    "Keep it concise and thoughtful. Don't include any usernames, hashtags, links or emojis."
)
