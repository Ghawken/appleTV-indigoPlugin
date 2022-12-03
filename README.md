# AppleTV indigoDomo Plugin

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Resources/icon_small.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Resources/icon_small.png?raw=true)

Hi all,

This is a indigodomo appleTV plugin for remote control and monitoring of activities of your apple devices.

It uses the pyatv library (many thanks!) and this needs to be installed via a pip3 terminal command before usage.  (Packaging it wasn't an option unfortunately as to many depencencies)

It use the pyatv PushListeners for playback activities to be immediately 'pushed' to the plugin devices.  No polling required.
This means if have lights dimming up on pause - it should happen immediately!

But before anything

In a terminal window enter:

#### `pip3 install pyatv`

Double click the release indigoplugin File and install.

All going well - nothing will happen...

If you get a ton of red/errors.  
You will need to install Command line tools for Xcode.   It is because of the dependencies of pyatv is miniaudio which requires Clang to be installed to compile.
See FAQ at bottom. 
Can try:  The below terminal command - if also fails see FAQ for manual method.
`xcode-select —install`

### Steps:

#### Go to PluginConfig

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/pluginConfig.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/pluginConfig.png?raw=true)

This one above.
Press the "Generate AppleTV Devices" - with some options if devices not found.

Options:
Force Discovery of all Devices:
This will create indigo devices for all airplay devices the plugin via library pyatv can find.
Any non-appleTV/Homepods (untested) will not function and ideally should be deleted.
THis is needed for the newer appleTV devices which are registered as yet such as 4k Gen 3 appleTV

Scan a single IP address
If your device is not found without using this option, you can enter its IP address and being a unicast scan based on IP
This is more robust that a wider network multicast scan.
If you device is not found with multicast, but correctly found with unicast you should assign it a fixed IP address
(router level - outside of plugin)
If not, when it's IP changes the plugin will loose it altogether.

Generate AppleTV Devices
Using the options above.
This will search your network for appleTV device and generate plugin Devices corresponding.
These devices will be located in the main device folder, but can be moved anywhere you like later.
You can re-press and re-press the button (if you like), and new devices should not duplicate.

#### Devices

Next go to a Device:

Open a device, with the Edit Device Details

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceConfig.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceConfig.png?raw=true)

You should see the above.

Since OS16 and Apple4k you will need to pair your indigoplugin Device with your appleTV

#### Steps:
Press the Start Pairing Button.

The plugin should find and connect to your appleTV.

A pincode should be displayed on the screen.

Enter the Pincode in the box, and press submit Pincode (Press) Button.

You should receive confirmation that pairing has been successful.

Press the SAVE button on the Config Dialog.

(I believe we need to do this only once... but time will tell...)

### Device Details

I expose a number of playback states (Thanks Karl for the typing on these!)

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceStates.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/DeviceStates.png?raw=true)

You will also see the device is an Indigo Relay - so there are Turn On/Turn Off/Toggle buttons that power down/power on the relevant appleTV.

### Remote Control / Actions

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/remoteNew.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/remoteNew.png?raw=true)


### ! New Version 0.0.15

Exposes all command options supplied by very helpful pyatv library.  Progammatically creates menu, so if more down the track should be available.
Allows sending of arguments with remote command
To enable:
Seeking to set position
Set Volume (if supported)
and Play URL

For most commands the optional arguments should be left blank, however can select double tap, hold etc. as the Dialog

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/Action.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/Action.png?raw=true)


### Launch App

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/lauchApp.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/lauchApp.png?raw=true)

I have also implemented Launch App - which allows you to launch a specific application of the appleTV.  

Unfortunately it doesn't allow LiveTV within the app, or more detailed control - but this can be managed with a lauchApp command, and then, left, down, down, select remote commands for example




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

Currently I expose all airplay devices - Sonos included.  I do not believe these can be controlled or report status - but have not specifically tested them.
The AppleTV devices are those we are aiming to support here.
No longer - by default only appleTV devices are generated.  Use the forceDiscovery option to enable creation of all devices found.


See here for more related to pyatv library

## https://pyatv.dev/support/faq/

# Changelog

Additional Remote control states - allow arguments to be sent.
Enabling set volume, double tap, hold, play_URL etc.
MenuItem: Add Logging info to show all Commands possible (not available!)
MenuItem: Add Logging info to show Features available for each Device
Remove unrecognised devices from being created.  (Tested Sonos devices can't work use Airplay2, and unknown encryption)
Should allow AppleTVs (all) and HomePods (untested)
Restart Device after pairing (avoiding need to restart plugin if connection issues)
Fine tuning some aspects.
More repeated reporting of PowerState

0.0.22
Fix for debug1 not turning off until 

0.0.23

Move to unicast connection for those devices that have a IP
(may help with intermittent connection issues)
Alternate back to multicast after 3 failures.
Messaging around commands being sent with arguments when they shouldnt
Move back to standard indigo file Logging given issue resolved.

0.0.24
Remove support for MRP disabled in OS16 and causes authentication failures

0.0.25
Re-Add MRP support, IF device supports it - without it PowerState Reporting fails/is not reliable.  It seems that MRP state is being depreciated by apple so may go completely in future.
More debug logging of service setup.

0.0.26
Add pluginConfig option for unicast scanning of a single IP address for device creation.
Useful with multicast fails to find device without power cycle
Update images

0.0.27
Add action to download artwork





