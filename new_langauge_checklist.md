Adding a new language
=====================

1. Create directory weeklypedia/static/archive/<lang>
2. Create new mailchimp list and configure the signup page
  1. List name: __ Wikipedia Edition
  2. From: weeklypedia@hatnote.com / Weeklypedia Digest
  3. How you got on our list: `You are receiving this because you signed up for weekly updates about active topics on __ Wikipedia.`
  4. Signup title: `<div style="text-align: center;"><span style="text-align:center">Weeklypedia (__ Edition)</span></div>`
  5. Signup content: `<div style="text-align: center;"><em>A list of the most edited Wikipedia articles and discussions from the last week.</em><br />
<a href="http://weekly.hatnote.com/" target="_blank">Learn more</a></div>`
  6. Signup background: #eeeeee
  7. Signup elements: Let people choose between HTML and plain text; only collect email address
  8. Remember the list id and signup url
3. Add the list id to secrets.json
4. Add the lanugage code to `SUPPORTED_LANGS` and signup url in `SIGNUP_MAP` in weeklypedia/common.py
5. Add crontab entries for fetching and publishing
6. Add an li for your signup to static/index.html (so we can get subscribers today)
7. Add an li for your signup to weeklypedia/issue_templates/template_index.html (so we can get subscribers next week), and add an li for the archive
