# All Hail Chaos
A bot I developed during quarantine

## Setting up
### data.py

You need to rename the file `data/data_example.py` into `data/data.py`, and then change some values :

```python

bot.token = "THE BEAUTIFUL TOKEN OF MY DISCORD BOT" #<- Place your bot token here. You can obtain one at Discord's developer portal : https://discordapp.com/developers/applications

bot.log_channel_id = 00000000000000000 #<- The ID of the channel you want the bot to output the logs to

bot.suggestion_channel_id = 00000000000000000 #<- The ID of the channel you want the bot to output the suggestions to

bot.ksoft_client = ksoftapi.Client("MY KSOFT.SI TOKEN", bot.loop) #<- Get a Ksoft.si token : https://api.ksoft.si/

bot.discord_rep = "MY DISCORDREP TOKEN" #<- Get a DiscordRep token : https://discordrep.com/

bot.nasa =  "I AM HACKING THE NASA" #<- Get a NASA API token : https://api.nasa.gov
```

Note that this is the minimal configuration required by the bot to run. More parameters can be defined in this file.

### Lavalink
To use Lavalink and the Music cog, please install Java 13 and run lavalink.bat before launching the bot (you may need to change the path to the app in the file's code). If you're not under Windows, just run these to commands :

```bash

$ cd All-Hail-Chaos
$ java -jar Lavalink.jar
```

Replace `All-Hail-Chaos` by the name and path of the folder in which both files Lavalink.jar and application.yml are in.

## Additionnal information
For more information about how to use the bot, check [my top.gg page](https://top.gg/bot/636359675943583775)
