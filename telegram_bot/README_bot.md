## Intro
This script allows you to send the content of a .txt file to yourself on Telegram. Follow the steps below to set it up.
WARNING: requires "requests" module. Use "pip3 install requests" if necessary. If you are using the ISIS-downloader you already
have "requests" installed on your system.

## How to make a bot
Add @Botfather on Telegram and follow the instructions to setup your own bot.
Save the token he will give you. Now add your Bot on Telegram.


## How to get your chat id
Using Telegram, send  "/my_id" to your bot.
Open "https://api.telegram.org/botXXX:YYYY/getUpdates" (replace XXX:YYYY with your bot token).
Under "chat" you will find your chat_id. Save it.


## How to Setup your Bot
Open bot_data.txt with a text-editor and insert your token and chat_id in their designated fields at the top. Do nut use whitespaces!
Your are now finished. execute "python3 bot.py <bot_data> <file_you_want_to_send>" to send the content of your file
to yourself. Mute the bot inside Telegram, if you do not want notifications.

Example: python3 bot.py bot_data.txt myfile.txt
