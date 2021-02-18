# All Hail Chaos
A bot I developed during quarantine

## How to self host Chaotic Bot

### Docker

**Docker coming soon!**

## Manual configuration and hosting

You're going to need a Discord bot account to run it. Here's how to do it.

### Creating a bot app on discord

- Create bot on Discord's bot portal
- Make a New Application
- Go to Bot settings and click on Add Bot
- Give Administrator permission to bot
- You will find your bot TOKEN there, it is important that you save it
- Go to OAuth2 and click bot, than add Administrator permissions
- You can follow the link that will appear to add the bot to your discord server

### Configuration info
This bot has only one configuration file, `data/data.py`, that we are going to fill from top to bottom in this guide.
To use it rename it from `data_sample.py` to `data.py`

### API Keys

This bot uses various APIs, for which you'll need tokens.

- [DiscordRep](https://discordrep.com/)
- [Ksoft](https://api.ksoft.si/)
- [NASA](https://www.nasa.gov/)


## Additional compulsary dependencies

### PostgreSQL

Install PostgreSQL, then create a user and a database dedicated to the bot.

Copy the credentials in the `postgre_connection` dictionary.

Then, execute the statements in the `database.sql` file.
This file assumes that the bot's role is named **chaotic**. If you named it something else, replace with the name used at every occurrence.

### Lavalink

Lavalink is a Java music server. It requires Java 13 (other versions pose various issues and aren't fully supported), so make sure that you run it with the right version.

Lavalink's configuration file is `application.yml`. If you intent to run it on the same server as the bot, then you won't have to edit anything for it to work.

If that's not the case, make sure to select a secure password (I personally recommend using sha-256 on a random string to generate strong passwords), and to fill appropriately the `lavalink_credentials` dictionary.

To run Lavalink itself, you'll need to do :

```bash
$ cd All-Hail-Chaos
$ java -jar Lavalink.jar
```

I highly recommend you to setup Ipv6 rotation (see Optional Configuration)

## Optional configuration

You can change the default bot prefix (it can be changed on a per-guild basis through a command).

I highly recommend you to create a support server for your bot. The default invite redirects to my server, which you're of course free to join.

You can also setup a channel for suggestions, and another for contact.

### Discord Bot lists

There is support for four major bot lists :

- [Top.gg](https://top.gg/)
- [Discord Bots](https://discord.bots.gg/)
- [Bots on discord](https://bots.ondiscord.xyz/)
- [Discord Bot List](https://discordbotlist.com/)

### GitHub

You can link your fork of this bot, allowing users to setup a hook to get the latest commit informations through the `github` command.

### Logging

You can get detailed statistics of command usage and servers by creating the tables in the `stats.sql` file and enabling the `bin/stats.py` file (un-comment line 49 of data/data.py).

For visualizing this data, I recommend [Grafana](https://grafana.com/), which creates amazing graphs.

### Database manipulation

To manipulate the database, like creating tables, etc..., I recommend you to use `OmniDB`, a web-based solution.

### Ipv6 rotation

Let's end this guide with what I deem the most important point : Ipv6 rotation.

Let me explain : Lavalink plays music from various sources, mainly Youtube. However, Youtube doesn't like people listening to its content through separate application. It therefore ratelimits people.

What this means is that, with your current configuration, sooner or later (and rather sooner than later), you won't be able to play music anymore, getting 429 errors.

The solution is to change your IP address, and that's where Ipv6 rotation comes into play :
The idea is simple : having so many different IPs that Youtube can't ban them all.

You will need at least a /64 IP block.

If you don't have one, check [This guide](https://ramblings.fred.moe/2020/3/tunnelbroker-with-lavalink)

If you have one, assuming it's /64, head to `application.yml` locate those lines and uncomment them :

```
#ratelimit:
  #ipBlocks: ["1.0.0.0/8", "..."] # list of ip blocks
  #strategy: "RotateOnBan" # RotateOnBan | LoadBalance | NanoSwitch | RotatingNanoSwitch
```

Put your ip Block under ipBlocks, and, for /64, select the strategy "NanoSwitch".

With that, you'll be able to fully enjoy your music

### Contact

If you have any questions, or if you'd want to report a broken step in this guide, either create an issue, or head on to [my Discord server](https://discord.gg/eFfjdyZ)

I know this guide is far from perfect, so if you see anything that needs to be clarified, added, or changed in any way, feel free to make a Pull Request.
