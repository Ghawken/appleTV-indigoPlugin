# Updates 2025

## Pre release 1.6.14

**1.6.14**

Add progressBar art saving.  Both automatically when updates available, and as a actionGroup
Width, and Colour modifiable.

Important: Fix for Async issues/timeout on disconnections (primarily seen when stopping/starting the appleTV connection)

Add artwork Modify options:
None - no change
Size - Modify and fix aspect ratio for CP use
Grayscale - On Paused greyscale artwortk
Overlay - Overlay default (user modifiable) paused symbol to artwork when paused.  (see paused image in Pictures directory)
eg.
![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/Paused-Example.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/Paused-Example.png?raw=true)



![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceConfig.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceConfig.png?raw=true)


Fixes and changes for above. 


**1.6.11**

Set Error status when connection lost/disconnected or not able to be made in Indigo

**1.6.10 -> 1.6.6**
[Reverted]
Attempt to push timed updates - however they don't exist.  All the updates being received are all the updates the appleTV is sending.  No point in a timed update.  If long delays between now playing updates (position etc.) on appletv.   Any user interaction stop/pause/play/volume is immediately reported.   Other passive updates - position of current playback - appears pretty intermittent...

**1.6.6**

Filter out non printable Emoji characters and check for (null) may be impacting some apps reporting Title of playback

Add device_state = Finish time of currently playing item.  eg. 3:45PM
Add device state = Remaining time of currently playing item eg. 1 hr 32 mins
Add device state = Percentage Complete of currently playing item eg. 32.1%

Fixes for logging/errors/exceptions logging for devices that don't support artwork (HomePods) Sonos Speakers and Airplay2 speakers
Move to empty strings for device states that are unreported.  Rather than None or Not Available

**1.6.5**

Further testing OS18.4 Companion changes, requiring seperate ID.   (May need repairing once..)
Add Multiple Simple Commands to Action menu selection  - Top menu, App Switcher, Scren Saver, Skip Forward, Skip Backward, Swipe Left, Right, Up and Down
Bug fix:  Check for Screen Saver active and turn off if playback command selected.  Previously would have to do this manually.

**1.6.0**

Extension of below Artwork addtitions/changes:  Add Artwork Modify Option
This greyscales the provided artwork when paused.

It also resizes the provided artwork to a transparent background box width and height is that set in widith (eg square)
This enables aspect ratio to remain intact for refreshingUrl control page use.

Add AppleTV device settings for Artwork - always updating the artwork if enabled and artwork changes.  Updates on PowerState changes and PlayState changes.   Removes need for Indigo based triggers on playback changes.


![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceConfig.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceConfig.png?raw=true)


Automatically changes artwork thumb if playing, or paused or nothing=everything else.

These files can be changed in the /Pictures directory once they exist and won't be changed.  If wish to go back to plugins default, delete the files and restart the plugin.

Update library - including recent unmerged pull to fix 18.4 companion issue (tested on tvOS 18.4).  Will merge to latest version when released

Update dependencies.

Move default artwork thumbnail (which is used when no playback) to Pictures directory.  On start if doesn't exist will create.  Can be user updated to whatever thumb suits

Update DeviceConfig.png

**1.5.14**

Add AppleTV device settings for Artwork - always updating the artwork if enabled and artwork changes. Updates on PowerState changes and PlayState changes. Removes need for Indigo based triggers on playback changes.

Automatically changes artwork thumb if playing, or paused or nothing=everything else.

These files can be changed in the /Pictures directory once they exist and won't be changed. If wish to go back to plugins default, delete the files and restart the plugin.

Update library - including recent unmerged pull to fix 18.4 companion issue (tested on tvOS 18.4). Will merge to latest version when released

Update dependencies.

Move default artwork thumbnail (which is used when no playback) to Pictures directory. On start if doesn't exist will create. Can be user updated to whatever thumb suits

Update DeviceConfig.png

**1.5.10**

Change to animate default artwork thumb for use in Kiosk Home use, or any web viewer of CP
Remove Nowplaying details when power off (avoids some persisting given variability in appleTV apps)

**1.5.8**

Add Default Artwork Thumbnail - use this if None or artwork not available. Allows when Artwork changing from something --> Nothing playing, returns back to this artwork.

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Server%20Plugin/images/apple-tv-default-thumb-playing.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Server%20Plugin/images/apple-tv-default-thumb-playing.png?raw=true)![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Server%20Plugin/images/apple-tv-default-thumb-paused.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Server%20Plugin/images/apple-tv-default-thumb-paused.png?raw=true)


# Called appleTV plugin, but supports AirPlay2 devices (!)
- Live reporting of current state/Playback/Pause and all actions of appleTV- HomePod Control
- AirPlay 2 compatible Speakers
- AirPlay 2 compatible Receivers

Plus speech to these devices as needed/with variable and device substitution.
Plus playback of URL and streams - Doorbell/Camera streams etc.

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Resources/icon_small.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Resources/icon_small.png?raw=true)


!
##


# AppleTV device, HomePod device and Airplay2 Speaker Plugin for Indigo

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Resources/icon_small.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Resources/icon_small.png?raw=true)

##
### AppleTV device, HomePod device and Airplay2 Speaker Plugin for Indigo

Instructions Updated for Version 1.2.0:

### Major Changes:
#### Play URL command
Fixes play URL command for >OS16.4 - can't get BI camera streams working, but https:// mp4 and mu38 play well.
(if particularly file doesn't play will relate to compatible file settings)

#### Airplay2 Speaker Support
Adds Airplay2 Speaker Support - allows playback of file to all Airplay2 devices.
Allows creation of indigo device for Airplay2 Speaker, and then file playback to these devices, including all Sonos Speakers that I have tested.
(Note does not allow control of Airplay2 devices, just playback, further control will likely follow)


### Plugin Setup

It uses the pyatv library (many thanks!) and this needs to be installed via a pip3 terminal command before usage.  (Packaging it wasn't an option unfortunately as to many depencencies)

https://github.com/postlund/pyatv


It use the pyatv Push Listeners for playback activities to be immediately 'pushed' to the plugin devices.  No polling required.
This means if have lights dimming up on pause - it should happen immediately!

Potential Uses:

Create Indigo devices for Speakers, appleTVs or Homepods.  Pair you appleTV and HomePod devices.  Once paired, Indigo receives immediate updates on status/play/pause being the most basic.

Enables:
1. Dim Lights on playback, turn on lights with pause with immediate response
2. Launch a particularly App on the appleTV, via Indigo as action
3. Annouce across one or all HomePods - either a mp3 file, or a Device State/Variable or text which will be read out in the current OSX system voices.
4. Playback mp3 files to Airplay2 speakers eg. Sonos and cheaper equivalents...

###Installation

Download and double click Plugin Bundle

Potential issue:
You may need to install Command line tools for Xcode.   It is because of the dependencies of pyatv is miniaudio which requires Clang to be installed to compile.
**See FAQ at bottom of this page if ongoing issues**
Can try:  The below terminal command - if also fails see FAQ for manual method.
`xcode-select —install`


### Steps:

#### Go to PluginConfig

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/pluginConfig.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/pluginConfig.png?raw=true)

This one above.
Press the "Generate AppleTV Devices" - with some options if devices not found.

Options:

**Force Discovery of all Devices**:

This seems to be required for more new OS devices.  Default should be enabled.

This will create indigo devices for all airplay devices the plugin via library pyatv can find.

Now Homepods will be appropriately named and created, as will all Airplay2 compatible devices.

**Scan a single IP address**
If your device is not found without using this option, you can enter its IP address and being a unicast scan based on IP
This is more robust that a wider network multicast scan.
If you device is not found with multicast, but correctly found with unicast you should assign it a fixed IP address
(in your router level - outside of plugin)
If not, when it's IP changes the plugin may loose it altogether.

**Generate AppleTV Devices**
Using the options above.
This will search your network for appleTV device and generate plugin Devices corresponding.
These devices will be located in Indigo's main device folder, but can be moved anywhere you like later. 
You can re-press and re-press the button (if you like), and new devices should not be duplicated (unless you have deleted them)

### Devices

Following the above generation of devices, all devices will be in the main Indigo Device directory.  Once created they can be moved to whereever makes sense.

Next go to a Device:

Open a device, with the Edit Device Details

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceConfig.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceConfig.png?raw=true)

You should see the above.

Since OS16 and Apple4k you will need to pair your indigoplugin Device with your appleTV

Some devices do not need to be paired (such as Homepods), but they still need to be connected. 

The Start Connection button below will setup them up for use


#### Steps:
Press the **Start Connection** Button.  And keep an eye on the Indigo Log where info will be displayued.

The plugin should find and connect to your appleTV device, or Homepod.

If a pincode is needed the Indigo log will let you know.  If not needed when prompted press SAVE and close the dialog.

Otherwise on the appleTV device - A pincode should be displayed on the screen of the appleTV device.

Enter the Pincode in the box, and press submit Pincode (Press) Button.

You should receive confirmation that pairing has been successful in the log.

Press the SAVE button on the Config Dialog.

(I believe we need to do this only once... but time will tell...)

**For Homepods:**

Simply press the Start Connection button, observe the indigo log for confirmation of setup and then click Save, once given okay to do so.

### Device Details

I expose a number of playback states (Thanks Karl for the typing on these!)

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceStates.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceStates.png?raw=true)

You will also see the device is an Indigo Relay - so there are Turn On/Turn Off/Toggle buttons that power down/power on the relevant appleTV.
(caveat here is power reporting is not perfect)

### Remote Control / Actions

I have choosen to exposes **all command** options supplied by very helpful pyatv library.  We Progammatically creates command menu, so if more options with library updates, down the track should be immediately available.
Allows sending of arguments with remote command
To enable:
Seeking to set position
Set Volume (if supported)
and Play URL

For most commands the optional arguments should be left blank, however can select double tap, hold etc. as per the Dialog

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/remoteNew1.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/remoteNew1.png?raw=true)

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/remoteNew2.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/remoteNew2.png?raw=true)
### Actions Available

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/Action.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/Action.png?raw=true)

### Launch App

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/lauchApp.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/lauchApp.png?raw=true)

I have also implemented Launch App - which allows you to launch a specific application of the appleTV.  

Unfortunately it doesn't allow LiveTV within the app, or more detailed control - but this can be managed with a lauchApp command, and then, left, down, down, select remote commands for example

### Save current Artwork

This AG will save the current artwork for the selected appleTV if it exists.


### Homepod Special Actions

Add an Action Group to Send Text to Speech annoucement to HomePods with current OSX System voice
(Change current voice in Macs OSX settings voices)

Allows Device and Variable subsitution so can read weather forcast etc. depending on setup

NEEDS ffmpeg (included in plugin), need to run quaranatine command on new install

Converts text to speech with system say command and then converts to mp3 for playback. Add a slight delay but seems to be under a second in my testing.


![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/SpeakAnnoucement.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/SpeakAnnoucement.png?raw=true)

### Homepod Stream File

This enables Homepod playback of a mp3 file.  There are quite specific file aspects that the HomePods like, primarly mp3.

Stream_File, or the Remote setting:

"Stream local file or remote file to device"

e.g:
Optional Argumment:
https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3

or
Local file: (like)
/Users/Indigo/Desktop/doorbell-1.mp3

You can pre-generate yuou own voice files as needed, if do not wish to use the action Group as above:
To do so
To generate voice file:
In terminal
`say "Person arrived Home" -o personhome.aiff`

This aiff generated file needs to be converted to mp3 files
ffmpeg, which is a commandline tool can convert say generated aiff

The follow command gives appropriate mp3 output to use.
`ffmpeg -i Input.aiff -f mp3 -acodec libmp3lame -ab 192000 -ar 44100 Output.mp3`

Use Output.mp3 in the "Stream local file or remote file to device"

### FAQ / Troubleshooting

#### pip3 install pyatv

Fails - with some red lines and an error about a dependency miniaudio (which we don't use...)
It appears to want to install some x-code "command line developer tools" -- commandline tools  - to help build this dependency.
Install the xcode components, appears to be usr/bin/clang and hopefully will able to be installed.

Oh No - it looks like needs 14gig of Xcode for this to work.  What a pain.
Try:
https://developer.apple.com/download/more/
Login and download Command Line Tools for Xcode and install.

The above worked for my production machine - which hit this issue.  (avoided Xcode install thankfully)

#### Can't remote control certain device.

Currently I expose all airplay devices - Sonos included.  I do not believe these can be controlled or report status.
Confimred these use AirPlay2 which has not been reverse engineered, we use Airplay1 here.
The AppleTV devices are those we are aiming to support here.
No longer - by default only appleTV devices are generated.  Use the forceDiscovery option to enable creation of all devices found.

#### See plugin Config menu for option Log AppleTV

This gives a few options of logging information for particuarly appletv that may help troubleshooting issues

See here for more related to pyatv library

## https://pyatv.dev/support/faq/











