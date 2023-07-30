<img src="https://github.com/neosheo/Stringwave/blob/main/screenshots/Screenshot_20230729-185203_1.png?raw=true" width="300" height="550" />
<img src="https://github.com/neosheo/Stringwave/blob/main/screenshots/Screenshot_20230729-185141_1.png?raw=true" width="300" height="550" />
<img src="https://github.com/neosheo/Stringwave/blob/main/screenshots/Screenshot_20230729-185245_1.png?raw=true" width="300" height="550" />
<img src="https://github.com/neosheo/Stringwave/blob/main/screenshots/Screenshot_20230729-185308_1.png?raw=true" width="300" height="550" />

# What it is.

Stringwave is an automated, self-hosted radio platform designed to emulate the 'Release Radar', 'Discover Weekly', and 'Liked Songs' playlists from Spotify. There are 2 python programs within it, Cogmera and Pipefeeder. Cogmera allows users to create 'Configs' which allow you to select genres, styles, decade, year, country, etc to find new music. Pipefeeder will allow you to subscribe to a youtube channel and get new music when it comes out. StringWave has 2 stations, new and main. All newly downloaded songs are automatically streamed to your new station. If you like a song you can move it to your main station.

# How to get started.

Simply git clone the repository and then cd into the new directory. You will need to create 3 files in here: icecast.xml, ezstream-new.xml, and ezstream-main.xml (examples are provided in repo, you can copy the example configs into the config directory. Make sure to change the passwords, note that source password in icecast.xml should be the same as the passwords in the ezstream configs) and run build.sh. Windows and Mac users may need to modify the build.sh file to make it work on your OS. If you are using a domain name make sure to add it to nginx.conf before running.

# How to use.

When you access the webapp there will be multiple options. 'New Music' is your stream for newly downloaded tracks. 'New Tracks' lists all the songs on the new station and gives you the option to delete them or move them to the main station. 'My Music' is where all the music you have moved from the new station is streamed. 'My Tracks' is the same as 'New Tracks' but for the main station. 'My Subscriptions' is where you can subscribe to YouTube channels. Just paste a YouTube channel link into the text box and press 'Subscribe.' You can also scroll through your subscriptions and unsubscribe to remove them. 'My Configurations' shows all your current configurations and allows you to delete configurations as well. 'New Configuration' allows you to add configurations.

# Things to keep in mind.

The skip button on the radio stations typically causes the stream to freeze and requires a refresh of the page to get the station started again so for now don't rely too much on this function.

Configurations cannot have a year and a decade so only choose one.

If you don't want to stream the new music and just want to download the new music, comment out lines 9-14 and lines 21-25 in scripts/run_radio.sh before running. Using syncthing in conjunction with this feature works well to move the music from your server to a phone or laptop.

# Future features.

The following features are planned:

1. creating custom stations
2. moving and deleting tracks from the now playing screens
3. adding songs manually to the radio
