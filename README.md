# AppleTV indigoDomo Plugin

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Resources/icon_small.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/appleTV.indigoPlugin/Contents/Resources/icon_small.png?raw=true)

Hi all,

This is a indigodomo appleTV plugin for remote control and monitoring of activities of your apple devices.

It uses the pyatv library (many thanks!) and this needs to be installed via a pip3 terminal command before usage.  (Packaging it wasn't an option unfortunately as to many depencencies)

It use the pyatv PushListeners for playback activities to be immediately 'pushed' to the plugin devices.  No polling required.
This means if have lights dimming up on pause - it should happen immediately!

But before anything

In a terminal window enter:

#### `sudo pip3 install pyatv`

Double click the release indigoplugin File and install.

All going well - nothing will happen...

### Steps:

#### Go to PluginConfig

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/pluginConfig.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/pluginConfig.png?raw=true)

This one above.
Press the "Generate AppleTV Devices"

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

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/RemoteCommands.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/RemoteCommands.png?raw=true)


The plugin exposes all remote control options via commands.

### Launch App

![https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/lauchApp.png?raw=true](https://github.com/Ghawken/appleTV-indigoPlugin/blob/master/Images/lauchApp.png?raw=true)

I have also implemented Launch App - which allows you to launch a specific application of the appleTV.  

Unfortunately it doesn't allow LiveTV within the app, or more detailed control - but this can be managed with a lauchApp command, and then, left, down, down, select remote commands for example





