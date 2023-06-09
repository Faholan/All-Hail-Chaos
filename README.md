# All Hail Chaos

A bot I developed during quarantine

# How to self-host Chaotic Bot

Start with cloning the repository in the folder of your choice.

The bot uses [poetry](https://python-poetry.org/) to manage dependencies.

You can install the dependencies with the following commands:

```bash

$ git clone https://github.com/Faholan/All-Hail-Chaos.git bot  # Clone the repository in a folder named `bot`
$ pipx install poetry  # Install poetry
$ cd bot  # Enter the bot folder
$ poetry install --no-dev  # Install the dependencies
```

This takes care of the Python dependencies. However, the bot still requires two other dependencies:

## Installing PostgreSQL

The bot uses [PostgreSQL](https://www.postgresql.org/) to store data. Install it with

```bash

$ sudo apt install postgresql
```

Create a new user and database for the bot, and execute the SQL commands in the file `database.sql` to create the
various tables used.

## Running Lavalink

The bot also uses [Lavalink](https://github.com/freyacodes/Lavalink) to stream music. If you don't want to play music,
you can skip this step,
but you will need to disable the music extension in the configuration.

The Lavalink executable is available in the `lavalink` folder.

You will need to install Java. Java 13 is the recommended version.

I recommend running Lavalink in the background with the use of systemd. This will allow Lavalink to start upon
booting your server so that you don't have to start it manually.

The sample configuration file is available under systemd/lavalink.service.

You just need to change the path to the lavalink folder in `WorkingDirectory`, allong with the `User` and `Group`
fields.

```bash

$ sudo -e /etc/systemd/system/lavalink.service  # Complete the config file based on the sample file
$ sudo systemctl enable lavalink  # Enable the service
$ sudo systemctl start lavalink  # Start the service
```

### Circumventing Youtube IP banning

Lavalink is great for streaming music, but unfortunately, YouTube doesn't like this pretty much.
Thus, if you continue streaming, you may find that the bot's IP has been blacklisted by YouTube.
Do not worry, this will only affect the bot, and not your personal use of YouTube. You may
end up having to fill a few Captchas, but that is about it.

However, your bot will be unable to play music anymore. If you want to be able to continue streaming,
you will need to change the IP adress the bot uses.

You will need to obtain what is called an IPv6 block. It is a list of IP adresses that Lavalink will cycle
through to connect to YouTube. The idea is that there are so many IPs in this block that YouTube cannot
possibly ban them all.

Unfortunately, I don't have a magic method of getting an IP block. This will depend on who exactly is your
hosting provider. If you plan on hosting the bot on a VPS, check right away if they have IPv6 blocks.

You can also try [this article](https://blog.arbjerg.dev/2020/3/tunnelbroker-with-lavalink), but I don't know whether it
works.
Please get in touch if you ever try it so that I can update this guide.

Let's for now assume that you have an IPv6 block, noted `fe80:beef::/64` (this is not the only size of IPV6 blocks.
Do not worry if you have another number after the slash.)

First of all, you need to allow Lavalink to use those IP adresses :

```bash
# Allow binding to the IPv6 block
$ sysctl -w net.ipv6.ip_nonlocal_bind=1
# Persist for next boot
$ sudo echo 'net.ipv6.ip_nonlocal_bind = 1' >> /etc/sysctl.conf
```

Next, you need to add this particular IP block to the list of allowed IP
adresses.

To make it easier, you can use the systemd service file provide in systemd/ipblock.service. Once again, write it down
in `/etc/systemd/system/ipblock.service`, and don't forget to replace <block/number> with your actual ip block, i.e
fe80:beef::/64 for example.

```bash
$ sudo -e /etc/systemd/system/ipblock.service  # Complete the config file based on the sample file
$ sudo systemctl enable ipblock  # Enable the service
$ sudo systemctl start ipblock  # Start the service
```

You will also need to edit a bit the `/etc/systemd/system/lavalink.service` file that we just created.
Replace `After=network.target` with `After=network.target ipblock.service`. That way, we will be sure that the Lavalink
service will only start after it can bind to those IP adresses.

You will finally need to edit the lavalink/application.yml file so that this section :

```yaml
    #ratelimit:
    #ipBlocks: ["1.0.0.0/8", "..."] # list of ip blocks
    #strategy: "NanoSwitch" # RotateOnBan | LoadBalance | NanoSwitch | RotatingNanoSwitch
    #searchTriggersFail: true # Whether a search 429 should trigger marking the ip as failing
    #retryLimit: -1 # -1 = use default lavaplayer value | 0 = infinity | >0 = retry will happen this numbers times
    #excludedIps: ["...", "..."] # ips which should be explicit excluded from usage by lavalink
```

now looks like this :

```yaml
    ratelimit:
      ipBlocks: [ "fe80:beef::/64" ] # list of ip blocks
      strategy: "NanoSwitch" # RotateOnBan | LoadBalance | NanoSwitch | RotatingNanoSwitch
      #searchTriggersFail: true # Whether a search 429 should trigger marking the ip as failing
      #retryLimit: -1 # -1 = use default lavaplayer value | 0 = infinity | >0 = retry will happen this numbers times
      #excludedIps: ["...", "..."] # ips which should be explicit excluded from usage by lavalink
```

If your IP block ends in /64 or a smaller number, then you can select strategy: "NanoSwitch".

__Wait, that's it ?__

Yes. You will now be able to use Lavalink without worrying about being IP banned.

Now that all the dependencies are installed and running, let's take a closer look at actually running the bot.

## Configuring the bot

All the configuration of the bot is in the data/config.toml file. Let's go over it line by line

### Bot section

#### token

This is the token of the bot, the way in which it authenticates to Discord.

Head over to [Discord](https://discord.com/developers/applications) to generate one.

Be aware that it must be kept secret! If somebody learns your bot's token, they will
be able to do whatever they want with it. If it ever gets leaked, you can head over to
[Discord](https://discord.com/developers/applications) to generate a new one and invalidate the
old one.

### log_channel_id

This is the channel in which the bot will log various messages.

This is also required. You'll need to activate Developer Settings in your Discord
client in order to get it. The bot will need permissions to send messages in this
channel.

### suggestion_channel_id

If you want to allow users to give you suggestions about the bot, you'll need to
fill in this ID.

### extensions

This is the list of extensions that the bot will load upon startup.

### invite_permissions

The permissions that the bot will require when invited to a new server.
This number can be calculated via the permission calculator available in the
application page on Discord's website.

### support

An invitation to join the bot's support server. It is currently filled with
the Chaotic Bot's invite link. Feel free to join too if you have any questions or
suggestions!

### privacy

This is the privacy policy of the bot, i.e., how you will handle the data stored
in the database.

### bot.command_tree section

This is an advanced configuration option. If you want to use a custom class for
the command tree instead of the default one, this is where you tell the bot
where to find it. Or you can change nothing and use the custom one developed by
yours truly.

### intents section

The intents required by the bot. This is a list of what events your bot
will be aware of. You don't need to change this list unless you want to change
the bot's code. In that case, check out [this page](https://discordpy.readthedocs.io/en/latest/api.html#intents) to know
what events each intent is for.

### database section

You cannot currently select type = "none", because I haven't implemented
having no database at all yet.

Fill in the various keys with the appropriate values for the bot to connect to
its postgresql database.

### GitHub section

This holds a link to the bot's public GitHub repository to check out the
source code.

### lavalink_nodes section

This is the list of nodes that the bot will use to connect to Lavalink.
If you are running multiple lavalink instances (aka nodes), you can add
various ones for different regions.

### apis section

This is where you will need to put the API keys used to provide the bot
with data from the Internet :

- [NASA](https://www.nasa.gov/)

### bot_lists section

If you have posted your bot in one of the bot lists indicated there, you
can put your token and a link to your bot's page there so that the bot will update your
server count automatically.

## Finally running the bot

You have two options to run this bot

1) You can simply use `poetry run python -m bot` to start the bot.
2) You can, guess what... Use yet another systemd service!

I love systemd. It works so nicely. Anyway, this config file is located is `systemd/chaotic.service`. You will need to
change the file paths in `WorkingDirectory` and `ExecStart` to match where exactly you put the bot.

However, don't do so just yet. As you may have seen, we start the bot using a mysterious `startup.sh` script.

This script allows the bot to start *after* Lavalink is up and running, otherwise it may run into issues.

This means that **if you don't run Lavalink**, you will need to comment out the first 3 lines of the script, so that
only the last line is uncommented.

**For everyone**, this last line will need to be edited. In the path, you will need to replace `user` with the actual
username of the user running this bot.

Now, you can edit the `/etc/systemd/system/chaotic.service` systemd file.

Just make sure, if you don't run Lavalink, to remove `lavalink.service` from Wants= and After= in the file.

```bash
$ sudo -e /etc/systemd/system/chaotic.service
$ sudo systemctl enable chaotic.service
$ sudo systemctl start chaotic.service
```

## Syncing the commands

You will have one final step to take before you can use the bot. Well, two, in fact.

1) Make sure that you have enabled the `cogs.owner` extension in your config file.
2) In Discord, in a channel the bot can see, say `@Bot sync` to synchronize the commands and have them available
   everywhere. You will only need to do this once.

### Contact

If you have any questions, or if you want to report a broken step in this guide, either create an issue, or head on
to [my Discord server](https://discord.gg/eFfjdyZ)

I know this guide is far from perfect, so if you see anything that needs to be clarified, added, or changed in any way,
feel free to make a Pull Request.
