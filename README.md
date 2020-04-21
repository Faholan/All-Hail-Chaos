# All Hail Chaos
A bot I developed during quarantine

## Setting up
### data.py

You need to rename the file `data/data_example.py` into `data/data.py`, and then change some values :

.. code:: py

    token="THE BEAUTIFUL TOKEN OF MY DISCORD BOT" #<- Place your bot token here (you can obtain one at [Discord's developer portal](https://discordapp.com/developers/applications))

    log_channel = 00000000000000000 #<- The ID of the channel you want the bot to output the logs to

    ksoft_token = "MY KSOFT.SI TOKEN" #<- Get a [Ksoft.si](https://api.ksoft.si/) token

    discord_rep = "MY DISCORDREP TOKEN" #<- Get a [DiscordRep](https://discordrep.com/) token

    dbl_token = None #<- If your bot is on [top.gg](https://top.gg), put your token here, or leave it to None

### Lavalink
To use Lavalink and the Music cog, please install Java 13 and run lavalink.bat before launching the bot (you may need to change the path to the app in the file's code). If you're not under Windows, just run these to commands :

.. code:: sh

    $ cd bot
    $ java -jar Lavalink.jar

In this example, the files Lavalink.jar and application.yml are in a folder named `bot`. They must be in the same folder for the Music Cog to work.

## Additionnal information

For more information about how to use the bot, check [my top.gg page](https://top.gg/bot/636359675943583775)
