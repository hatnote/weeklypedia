Adding a new language
=====================

# Create directory weeklypedia/static/archive/<lang>
# Create new mailchimp list and configure the signup page
## List name: __ Wikipedia Edition
## From: weeklypedia@hatnote.com / Weeklypedia Digest
## How you got on our list: `You are receiving this because you signed up for weekly updates about active topics on __ Wikipedia.`
## Signup title: Weeklypedia (__ Edition) 
## Signup content: `<div style="text-align: center;"><em>A list of the most edited Wikipedia articles and discussions from the last week.</em><br />
<a href="http://weekly.hatnote.com/" target="_blank">Learn more</a></div>`
## Signup background: #eeeeee
## Signup elements: Let people choose between HTML and plain text; only collect email address
## Remember the list id and signup url
# Add the list id to secrets.json
# Add the lanugage code to `SUPPORTED_LANGS` and signup url in `SIGNUP_MAP` in weeklypedia/common.py
# Add crontab entries for fetching and publishing
# Add an li for your signup to static/index.html (so we can get subscribers today)
# Add an li for your signup to weeklypedia/issue_templates/template_index.html (so we can get subscribers next week), and add an li for the archive
