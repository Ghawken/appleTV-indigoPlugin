#! /usr/bin/env python3.10
# -*- coding: utf-8 -*-

"""
Author: GlennNZ

"""

import threading
from enum import Enum
import traceback

import asyncio

from queue import Queue

import logging
from logging.handlers import TimedRotatingFileHandler

import time as time
from typing import Optional

try:
    import requests
except:
    pass

import time as t

try:
    import pyatv
    import pyatv.const
except:
    # error in init when can message
    pass

import sys
import os
from os import path

import logging

# import applescript
import xml.dom.minidom
import random
import shutil
from os import listdir
from os.path import isfile, join

try:
    import indigo
except:
    pass

try:
    import pydevd_pycharm
    pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True, suspend=False)
except:
    pass


################################################################################
# New Indigo FileHandler, only pass higher message and manage the string formatting issue
# where for some reason %s not substituted in filehandler, but in log without problem
################################################################################
class IndigoFileLogHandler(TimedRotatingFileHandler):
    def emit(self, record, **kwargs):
        try:
            levelno = int(record.levelno)
            if self.level <= levelno:  ## Don't do anything if level display is lower
                new_msg = f"{path.basename(record.pathname)}:{record.funcName}:{record.lineno}"
                record.msg =  f"{new_msg} : {record.msg}"
                record.args = None  ## This is the old string formatting %s issue.  Need to combine and then delete all args
                try:
                    if self.shouldRollover(record):
                        self.doRollover()
                    logging.FileHandler.emit(self, record)
                except Exception:
                    self.handleError(record)

        except Exception as ex:
            indigo.server.log(f"Error in Loggging FileHandler: {ex}")
            indigo.server.log(f"Error in Logging FileHandler execution:\n\n{traceback.format_exc(30)}", isError=False)
            pass
################################################################################
# New Indigo Log Handler - display more useful info when debug logging
# update to python3 changes
################################################################################
class IndigoLogHandler(logging.Handler):
    def __init__(self, display_name, level=logging.NOTSET):
        super().__init__(level)
        self.displayName = display_name

    def emit(self, record):
        """ not used by this class; must be called independently by indigo """
        logmessage = ""
        try:
            levelno = int(record.levelno)
            is_error = False
            is_exception = False
            if self.level <= levelno:  ## should display this..
                if record.exc_info !=None:
                    is_exception = True
                if levelno == 5:	# 5
                    logmessage = '({}:{}:{}): {}'.format(path.basename(record.pathname), record.funcName, record.lineno, record.getMessage())
                elif levelno == logging.DEBUG:	# 10
                    logmessage = '({}:{}:{}): {}'.format(path.basename(record.pathname), record.funcName, record.lineno, record.getMessage())
                elif levelno == logging.INFO:		# 20
                    logmessage = record.getMessage()
                elif levelno == logging.WARNING:	# 30
                    logmessage = record.getMessage()
                elif levelno == logging.ERROR:		# 40
                    logmessage = '({}: Function: {}  line: {}):    Error :  Message : {}'.format(path.basename(record.pathname), record.funcName, record.lineno, record.getMessage())
                    is_error = True
                if is_exception:
                    logmessage = '({}: Function: {}  line: {}):    Exception :  Message : {}'.format(path.basename(record.pathname), record.funcName, record.lineno, record.getMessage())
                    indigo.server.log(message=logmessage, type=self.displayName, isError=is_error, level=levelno)
                    if record.exc_info !=None:
                        etype,value,tb = record.exc_info
                        tb_string = "".join(traceback.format_tb(tb))
                        indigo.server.log(f"Traceback:\n{tb_string}", type=self.displayName, isError=is_error, level=levelno)
                        indigo.server.log(f"Error in plugin execution:\n\n{traceback.format_exc(30)}", type=self.displayName, isError=is_error, level=levelno)
                    indigo.server.log(f"\nExc_info: {record.exc_info} \nExc_Text: {record.exc_text} \nStack_info: {record.stack_info}",type=self.displayName, isError=is_error, level=levelno)
                    return
                indigo.server.log(message=logmessage, type=self.displayName, isError=is_error, level=levelno)
        except Exception as ex:
            indigo.server.log(f"Error in Logging: {ex}",type=self.displayName, isError=is_error, level=levelno)

################################################################################
# Use uniqueQueue to avoid multiple camera images pending
################################################################################
class UniqueQueue(Queue):
    def put(self, item, block=False, timeout=None):
        if item not in self.queue:  # fix join bug
            Queue.put(self, item, block, timeout)
    def _init(self, maxsize):
        self.queue = set()
    def _put(self, item):
        self.queue.add(item)
    def _get(self):
        return self.queue.pop()

####################################################################################
class appleTVListener( pyatv.interface.DeviceListener,pyatv.interface.PushListener, pyatv.interface.PowerListener):

    def __init__(self, plugin, loop, atv_config,deviceid):
        self.plugin = plugin
        self.plugin.logger.debug("Within init of AppleTVListener/all")
        self.deviceid = deviceid
        self.atv = None
        self.loop = loop
        self.atv_config = atv_config
        self._app_list = None
        self.all_features = None
        self._task = self.loop.create_task(self.loop_atv(self.loop, atv_config=self.atv_config, deviceid=self.deviceid))


    ## Add properties
    @property
    def power(self):
        if self.atv != None:
            return self.atv.power.power_state
        else:
            return ""

    @property
    def device_ID(self):
        if self.deviceid != None:
            return int(self.deviceid)
        else:
            return 0

    @property
    def app_list(self):
        if self._app_list != None:
            return self._app_list
        else:
            return ""


    async def async_lauch_app(self, app_id: str) -> None:
        """Select input source."""
        try:
            await self.atv.apps.launch_app(app_id)
        except:
            self.plugin.logger.exception("Launch App Error")

    async def _update_app_list(self):
        try:
            self.plugin.logger.debug("Updating app list")
            try:
                apps = await self.atv.apps.app_list()
            except pyatv.exceptions.NotSupportedError:
                self.plugin.logger.error("Listing apps is not supported", exc_info=True)
            except pyatv.exceptions.ProtocolError:
                self.plugin.logger.exception("Failed to update app list")
            else:
                self._app_list = {
                    app.name: app.identifier
                    for app in sorted(apps, key=lambda app: app.name.lower())
                }
                self.plugin.logger.debug(f"{self._app_list}")
        except:
            self.plugin.logger.exception("Update App list issue")

    def power_on(self):
        if self.atv !=None:
            self.plugin.logger.debug(f"send atc.power turn on command")
            self.loop.create_task(self.atv.power.turn_on())

    def power_off(self):
        if self.atv !=None:
            self.plugin.logger.debug(f"send atc.power turn off command")
            self.loop.create_task(self.atv.power.turn_off())


    def powerstate_update( self, old_state, new_state  ):
        self.plugin.logger.debug(f"powerstate update Old {old_state} and new {new_state}")
        device = indigo.devices[self.deviceid]
        if new_state == pyatv.const.PowerState.On:
            device.updateStateOnServer("onOffState", True)
            device.updateStateImageOnServer(indigo.kStateImageSel.PowerOn)
        elif new_state == pyatv.const.PowerState.Off:
            device.updateStateOnServer("onOffState", False)
            device.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)


    def _handle_disconnect(self):
        """Handle that the device disconnected and restart connect loop."""
        try:
            if self.atv:
                self.atv.close()
                self.atv = None
            if self._task:
                self._task.cancel()
                self._task = None
            self.sleep(0.2)
            self._task = self.loop.create_task(self.loop_atv(self.loop, atv_config=self.atv_config, deviceid=self.deviceid))
        except:
            self.plugin.logger.debugf("_handle disconnect and restart", exc_info=True)

    def disconnect(self):
        """Disconnect from device."""
        self.plugin.logger.debug("Disconnecting from device")
        self.is_on = False
        try:
            if self.atv:
                self.atv.close()
                self.atv = None
            if self._task:
                self._task.cancel()
                self._task = None
        except Exception:  # pylint: disable=broad-except
            self.plugin.logger.debug("An error occurred while disconnecting", exc_info=True)

    def connection_lost(self, exception: Exception) -> None:
        """Call when connection was lost."""
        self._remove()
        self._handle_disconnect()

    def connection_closed(self) -> None:
        """Call when connection was closed."""
        self._remove()
        self._handle_disconnect()

    def _remove(self):
        self.app["atv"].pop(self.identifier)
        self.app["listeners"].remove(self)

    def playstatus_update(self, updater, playstatus: pyatv.interface.Playing) -> None:
        """Call when play status was updated."""
        try:
            self.plugin.logger.debug("Playstatus Update Called")
            try:
                self.task.cancel()
            except:
                pass
            time_start = time.time()
            self.task = asyncio.create_task(
                self.plugin.process_playstatus(
                    playstatus,
                    self.atv,
                    time_start,
                    self.deviceid
                )
            )
        except:
            self.plugin.logger.exception("playstatus update exception:")

    def start_app(self, appid):
        try:
            self.plugin.logger.debug(f"Within start_app and appid - {appid}")
            self.loop.create_task(self.async_lauch_app(appid))
        except:
            self.plugin.logger.exception("Error in Start App")

    def send_command(self, command, **kwargs):
        try:
            self.plugin.logger.debug(f"Within send_command and command - {command}")

            if command == "turn_on":
                self.plugin.logger.debug(f"Command turn_on received: Powerstate:{self.atv.power.power_state}")
                self.loop.create_task(self.atv.power.turn_on())
            elif command == "turn_off":
                self.loop.create_task(self.atv.power.turn_off())
            else:
                self.loop.create_task(self.async_send_command(command))
        except:
            self.plugin.logger.exception("Error in send_command")

    async def async_send_command(self, command, **kwargs):
        """Send a command to one device."""
        #num_repeats = kwargs[ATTR_NUM_REPEATS]
       # delay = kwargs.get(ATTR_DELAY_SECS, DEFAULT_DELAY_SECS)
        try:
            command=command.strip(";")
            self.plugin.logger.debug(f"Within async send command.  Command {command}")
            if not self.atv:
                self.plugin.logger.info("Unable to send commands, not connected to %s", self.name)
                return
            attr_value = getattr(self.atv.remote_control, command, None)
            if not attr_value:
                raise ValueError("Command not found. Exiting sequence")
            self.plugin.logger.debug("Sending command %s", command)
            await attr_value()
            await asyncio.sleep(0.1)
        except ValueError:
            self.plugin.logger.info(f"This Command is not supported.  Command in question = {command}")
            self.plugin.logger.debug(f"Exception:",exc_info=True)
            return
        except pyatv.exceptions.NotSupportedError:
            self.plugin.logger.info(f"This Command is not supported.  Command in question = {command}")
            self.plugin.logger.debug(f"Exception:", exc_info=True)
            return
        except pyatv.exceptions.CommandError:
            self.plugin.logger.debug("Command Error in Send Command", exc_info=True)
            self.plugin.logger.info(f"Command Failed.  Command in question = {command}")
        except:
            self.plugin.logger.exception("Async send command exception.")

    def playstatus_error(self, updater, exception: Exception) -> None:
        self.plugin.logger.debug("Error in Playstatus", exc_info=True)


    async def connect_atv(self, loop, identifier, airplay_credentials):
        """Find a device and print what is playing."""
        try:
            atvs = await pyatv.scan(loop, identifier=identifier)
            if not atvs:
                self.plugin.logger.info("No devices found, will retry")
                return
            config = atvs[0]
            self.plugin.logger.debug(f"AppleTV:\n {config}")
            config.set_credentials(pyatv.Protocol.AirPlay, airplay_credentials)
            config.set_credentials(pyatv.Protocol.Companion, airplay_credentials)
            config.set_credentials(pyatv.Protocol.RAOP, airplay_credentials)
            self.plugin.logger.debug(f"Connecting to {config.address}")
            return await pyatv.connect(config, loop)
        except:
            self.plugin.logger.exception("Connect ATV Exception")

    async def loop_atv(self, loop, atv_config, deviceid):
        try:
            identifier = atv_config["identifier"]
            airplay_credentials = atv_config["credentials"]
            self.atv = await self.connect_atv(loop, identifier, airplay_credentials)
            if self.atv:
                listener = self
                self.atv.push_updater.listener = listener
                self.atv.listener = listener
                self.atv.power.listener = listener
                self.atv.push_updater.start()
                self.atv.listener.start()
                self.atv.power.listener.start()
                self.plugin.logger.debug("Push updater started")
                device = indigo.devices[deviceid]
                device.updateStateOnServer(key="status", value="Paired. Push Updating.")
                # Update app list
                self.plugin.logger.debug("Updating app list")
                self.plugin.logger.info(f"{device.name} successfully connected and real-time Push updating enabled.")
                await self._update_app_list()

            while True:
                await asyncio.sleep(20)
                try:
                    self.atv.metadata.app
                except:
                    self.plugin.logger.debug("Exception:", exc_info=True)
                    self.plugin.logger.debug("Reconnecting to Apple TV")
                    # reconnect to apple tv
                    self.atv = await self.connect_atv(loop, identifier, airplay_credentials)
                    if self.atv:
                        listener = self
                        self.atv.push_updater.listener = listener
                        self.atv.listener = listener
                        self.atv.power.listener = listener
                        self.atv.push_updater.start()
                        self.atv.listener.start()
                        self.atv.power.listener.start()
                        self.plugin.logger.debug("Push updater started")
                        self.plugin.logger.info(f"{device.name} successfully connected and real-time Push updating enabled.")
        except:
            self.plugin.logger.debug("Exception Loop:",exc_info=True)
################################################################################
class Plugin(indigo.PluginBase):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        ################################################################################
        # Setup Logging
        ################################################################################
        self.logger.setLevel(logging.DEBUG)
        try:
            self.logLevel = int(self.pluginPrefs["showDebugLevel"])
            self.fileloglevel = int(self.pluginPrefs["showDebugFileLevel"])
        except:
            self.logLevel = logging.INFO
            self.fileloglevel = logging.DEBUG

        self.logger.removeHandler(self.indigo_log_handler)
        self.logger.removeHandler(self.plugin_file_handler)
        self.indigo_log_handler = IndigoLogHandler(pluginDisplayName, logging.INFO)
        ifmt = logging.Formatter("%(message)s")
        self.indigo_log_handler.setFormatter(ifmt)
        self.indigo_log_handler.setLevel(self.logLevel)
        self.logger.addHandler(self.indigo_log_handler)
        log_dir = indigo.server.getLogsFolderPath(pluginId)
        log_dir_exists = os.path.isdir(log_dir)

        if not log_dir_exists:
            try:
                os.mkdir(log_dir)
                log_dir_exists = True
            except:
                indigo.server.log(u"unable to create plugin log directory - logging to the system console", isError=True)
                self.plugin_file_handler = logging.StreamHandler()
        if log_dir_exists:
            self.plugin_file_handler = IndigoFileLogHandler("%s/plugin.log" % log_dir, when='midnight', backupCount=5)
        pfmt = logging.Formatter('%(asctime)s.%(msecs)03d\t[%(levelname)8s] %(name)20s.%(funcName)-25s%(msg)s', datefmt='%d-%m-%Y %H:%M:%S')
        self.plugin_file_handler.setFormatter(pfmt)
        self.plugin_file_handler.setLevel(self.fileloglevel)
        self.logger.addHandler(self.plugin_file_handler)
        ################################################################################
        # Finish Logging changes
        ################################################################################
        logging.getLogger("Plugin.pyatv").setLevel(logging.THREADDEBUG)
        try:
            import pyatv
        except ImportError:
            raise ImportError("\n{0:=^100}\n{1:=^100}\n{2:=^100}\n{3:=^100}\n{4:=^100}\n{5:=^100}\n".format("=", " Fatal Error Starting appleTV Plugin  ", " Missing required Library; pyatv missing ", " Run 'pip3 install pyatv' in a Terminal window ", " and then restart plugin. ", "="))

        self.logger.debug(u"logLevel = " + str(self.logLevel))

        self._appleTVpairing = None ## single pairing - will not support pairing multiple appLeTVs at same time.  (Pairing that is - connection fine!)

        self.pluginStartingUp = True
        self.pluginDisplayName = pluginDisplayName
        self.pluginId = pluginId
        self.pluginVersion = pluginVersion
        self.pluginIndigoVersion = indigo.server.version
        self.pluginPath = os.getcwd()

        self.prefsUpdated = False
        self.logger.info(u"")

        self._paired_credentials = None
        self.appleTVManagers = []

        self.logger.info("{0:=^130}".format(" Initializing New Plugin Session "))
        self.logger.info("{0:<30} {1}".format("Plugin name:", pluginDisplayName))
        self.logger.info("{0:<30} {1}".format("Plugin version:", pluginVersion))
        self.logger.info("{0:<30} {1}".format("Plugin ID:", pluginId))
        self.logger.info("{0:<30} {1}".format("Indigo version:", indigo.server.version))
        self.logger.info("{0:<30} {1}".format("Python version:", sys.version.replace('\n', '')))
        self.logger.info("{0:<30} {1}".format("Python Directory:", sys.prefix.replace('\n', '')))
        self.logger.info("")
        self.pluginprefDirectory = '{}/Preferences/Plugins/com.GlennNZ.indigoplugin.appleTV'.format(indigo.server.getInstallFolderPath())

        # Change to logging
        pfmt = logging.Formatter('%(asctime)s.%(msecs)03d\t[%(levelname)8s] %(name)20s.%(funcName)-25s%(msg)s',
                                 datefmt='%Y-%m-%d %H:%M:%S')
        self.plugin_file_handler.setFormatter(pfmt)

        self.debug1 = self.pluginPrefs.get('debug1', False)
        self.debug2 = self.pluginPrefs.get('debug2', False)
        self.debug3 = self.pluginPrefs.get('debug3', False)
        self.debug4 = self.pluginPrefs.get('debug4', False)
        self.debug5 = self.pluginPrefs.get('debug5', False)
        self.debug6 = self.pluginPrefs.get('debug6', False)
        self.debug7 = self.pluginPrefs.get('debug7', False)
        self.debug8 = self.pluginPrefs.get('debug8', False)
        self.debug9 = self.pluginPrefs.get('debug9', False)

        if self.debug3:
            logging.getLogger("Plugin.HomeKit_pyHap").setLevel(logging.DEBUG)
        else:
            logging.getLogger("Plugin.HomeKit_pyHap").setLevel(logging.INFO)

        self._event_loop = None
        self._async_thread = None

        self.logger.info(u"{0:=^130}".format(" End Initializing New Plugin  "))



    def closedPrefsConfigUi(self, valuesDict, userCancelled):
        self.debugLog(u"closedPrefsConfigUi() method called.")
        if self.debug1:
            self.logger.debug(f"valuesDict\n {valuesDict}")
        if userCancelled:
            self.debugLog(u"User prefs dialog cancelled.")
        if not userCancelled:
            self.logLevel = int(valuesDict.get("showDebugLevel", '5'))
            self.fileloglevel = int(valuesDict.get("showDebugFileLevel", '5'))
            self.debug1 = valuesDict.get('debug1', False)
            self.debug2 = valuesDict.get('debug2', False)
            self.debug3 = valuesDict.get('debug3', False)
            self.debug4 = valuesDict.get('debug4', False)
            self.debug5 = valuesDict.get('debug5', False)
            self.debug6 = valuesDict.get('debug6', False)
            self.debug7 = valuesDict.get('debug7', False)
            self.debug8 = valuesDict.get('debug8', False)
            self.debug9 = valuesDict.get('debug9', False)

            self.indigo_log_handler.setLevel(self.logLevel)
            self.plugin_file_handler.setLevel(self.fileloglevel)

            if self.debug3:
                logging.getLogger("Plugin.HomeKit_pyHap").setLevel(logging.DEBUG)
            else:
                logging.getLogger("Plugin.HomeKit_pyHap").setLevel(logging.INFO)

            self.logger.debug(u"logLevel = " + str(self.logLevel))
            self.logger.debug(u"User prefs saved.")
            self.logger.debug(u"Debugging on (Level: {0})".format(self.logLevel))
        return True

    def deviceStartComm(self, device):
        self.logger.debug(f"{device.name}: Starting {device.deviceTypeId} Device {device.id} ")
        device.stateListOrDisplayStateIdChanged()

        if device.enabled:
            device.updateStateOnServer(key="status", value="Starting Up")
            device.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
            identifier = device.states["identifier"]
            credentials = device.ownerProps.get("credentials","")

            if credentials != "":
                self.logger.info(f"{device.name} Pairing Credentials exist, attempting to connect.")
                new_data = {}
                new_data["credentials"] = credentials
                new_data["identifier"] = identifier
                self.appleTVManagers.append( appleTVListener(self, self._event_loop, new_data, device.id ))

        else:
            device.updateStateOnServer(key="status", value="Starting Up")
            device.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)


    def startPairing(self, valuesDict, type_id="", dev_id=None):
        self.logger.debug(u'Start Pairing Button pressed Called.')
       # self.logger.debug(f"valueDict {valuesDict}\n, type_id {type_id}, and dev_id {dev_id}")
        self._appleTVpairing  = None
        device = indigo.devices[dev_id]
        identifier = device.states['identifier']

        # get all atvs
        self._event_loop.create_task(self.return_MatchedappleTVs(identifier))
        self.logger.info("Scanning for all AppleTVs")



    async def two_pairing(self, identifier, pincode):
        try:
            self.logger.debug(f"Second Step One Pairing Started {identifier} & pincode {pincode}")
            await self._appleTVpairing.finish()
            if self._appleTVpairing.has_paired:
                self.logger.debug(f"Paired with Credentials {self._appleTVpairing.service.credentials}")
                self._paired_credentials = self._appleTVpairing.service.credentials
                self.logger.info(f"Successfully Paired with appleTV. Please close Config window.")

            await self._appleTVpairing.close()

            return self._paired_credentials

        except pyatv.exceptions.PairingError:
            self.logger.error("Pairing Error.  Likely Incorrect Code please correct and try again")
            return
        except pyatv.exceptions.NotSupportedError:
            self.logger.info("Pairing Error.  Not Supported.  May not be needed.")
            return
        except:
            self.logger.exception("Two Pairing Exception")

    async def one_pairing(self, atv):
        try:
            self.logger.debug(f"First Step One Pairing Started {atv.identifier}")
            self._paired_credentials = None
            self._appleTVpairing = await pyatv.pair( atv, loop=self._event_loop, protocol=pyatv.Protocol.AirPlay)
            await self._appleTVpairing.begin()
            self.logger.info("Begin Pairing Started")
            if self._appleTVpairing.device_provides_pin:
                self.logger.info("This appleTV needs a Pincode.  Please enter and press Submit.")
        except:
            self.logger.exception("OnePairing")

    def submitCode(self, valuesDict, type_id="", dev_id=None):
        self.logger.debug(u'submit PINCode Button pressed Called.')
      #  self.logger.debug(f"valueDict {valuesDict}\n, type_id {type_id}, and dev_id {dev_id}")
        vercode = valuesDict['verficationcode']
        device = indigo.devices[dev_id]
        identifier = device.states['identifier']
        if vercode is None:
            self.logger.error("Please enter code")
            return

        self._appleTVpairing.pin(vercode)

        self._event_loop.create_task(self.two_pairing(identifier, vercode))

        return valuesDict

    ########################################
    # Indigo Device Startup
    def deviceStopComm(self, device):
        try:
            self.logger.debug(f"{device.name}: Stopping {device.deviceTypeId} Device {device.id}")
            device.updateStateOnServer(key="status", value="Off")
            device.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
            for i in range(len(self.appleTVManagers) - 1, -1, -1):
                if int(self.appleTVManagers[i].device_ID)== int(device.id):
                    self.appleTVManagers[i].disconnect()
                    del self.appleTVManagers[i]
                    self.logger.info(f"Removed AppleTV Manager for device: {device.name}")


        except:
            self.logger.debug("Exception in DeviceStopCom \n", exc_info=True)

    def validateDeviceConfigUi(self, values_dict, type_id, dev_id):
        try:
            self.logger.debug(f"ValidateDevice Config UI called {values_dict} and ID {dev_id}")
            return (True, values_dict)
        except:
            self.logger.exception("Error validate Config")
            return (True, values_dict)
    def runConcurrentThread(self):
        # Periodically check to see that the subscription hasn't expired and that the reflector is still working.
        try:
            self.sleep(1)
            self.sleep(5)
            self.pluginStartingUp = False
            self.sleep(10)

            while True:
                self.sleep(5)

        except self.StopThread:
            ## stop the homekit drivers
            self.logger.info("Completing full Shutdown ...")

        except:
            self.logger.debug("Exception in runConcurrentThread", exc_info=True)
            ## stop the homekit driver
            self.sleep(2)
            ## update all devices and start Bridge again.
            self.driver_multiple = []
            self.bridge_multiple = []
            self.driverthread_multiple = []
            self.update_deviceList()

    def startup(self):
        self.debugLog(u"Starting Plugin. startup() method called.")
        self.logger.debug("Checking Plugin Prefs Directory")
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        self._async_thread = threading.Thread(target=self._run_async_thread)
        self._async_thread.start()

    def shutdown(self):
        self.logger.info("Shutting down Plugin}")


    def validatePrefsConfigUi(self, valuesDict):

        self.debugLog(u"validatePrefsConfigUi() method called.")
        error_msg_dict = indigo.Dict()
        return (True, valuesDict)

        ## Generate QR COde for Homekit and open Web-Browser to display - is a PNG


    def toggleDebugEnabled(self):
        """
        Toggle debug on/off.
        """
        self.debugLog(u"toggleDebugEnabled() method called.")
        if self.logLevel == logging.INFO:
            self.logLevel = logging.DEBUG
            self.indigo_log_handler.setLevel(self.logLevel)

            indigo.server.log(u'Set Logging to DEBUG')
        else:
            self.logLevel = logging.INFO
            indigo.server.log(u'Set Logging to INFO')
            self.indigo_log_handler.setLevel(self.logLevel)

        self.pluginPrefs[u"logLevel"] = self.logLevel
        return
        ## Triggers


    ########################################
    # Menu Debug Items
    ########################################
    def show_internallist(self, *args, **kwargs):
        # Write all published devices to the event log with their friendly name
        self.logger.info(u"{0:=^165}".format(" self device_list_internal_idonly "))
        for device in self.device_list_internal_idonly:
            self.logger.info(f"{device}")
        self.logger.info(u"{0:=^165}".format(" self device_list_internal "))
        for device in self.device_list_internal:
            self.logger.info(f"{device}")
    ####

    ##
    def restartPlugin(self):
        # indigo.server.log(u"restart Plugin Called.")
        plugin = indigo.server.getPlugin('com.GlennNZ.indigoplugin.HomeKitLink-Siri')
        plugin.restart()

    def generate(self, values_dict, type_id="", dev_id=None):
        self.logger.debug("generate devices called")
        self._event_loop.create_task(self.get_appleTVs())
    #######################################
    ## More Menu Items
    #######################################
    def Menu_dump_accessories(self, *args, **kwargs):
        self.logger.debug("Dump accessories called...")
        self.logger.info(u"{0:=^130}".format(" Accessories Follow "))
        for num in range(0, len(self.bridge_multiple)):
            self.logger.info("*** Next HomeKit Bridge ***")
            if self.debug6:
                self.logger.debug("{}".format(self.bridge_multiple[num].accessories))
            self.logger.info("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in self.bridge_multiple[num].accessories.items()) + "}")

    def Menu_reset_pairing(self, *args, **kwargs):
        self.logger.debug("reset Paired Clients called...")
        self.logger.info("{}".format())

    #### Asyncio

    def _run_async_thread(self):
        self.logger.debug("_run_async_thread starting")
        self._event_loop.create_task(self._async_start())
        self._event_loop.run_until_complete(self._async_stop())
        self._event_loop.close()

    async def _async_start(self):
        self.logger.debug("_async_start")
        self.logger.info("Discovering Devices and setting up connection")
        # add things you need to do at the start of the plugin here

    def sendLaunchApp(self, valuesDict, typeId):
        self.logger.debug(f"send Lauch App Called {valuesDict} & {typeId}")
        props = valuesDict.props
        self.logger.debug(f"Props equal: {props}")

        if props["appleTV"] =="" or props["appleTV"]=="":
            self.logger.info("No AppleTV selected.")
            return

        appleTVid = props["appleTV"]
        apptoLaunch = props["apptoLaunch"]
        self.logger.info(f"Sending apptoLaunch {apptoLaunch} to appleTV Device ID {appleTVid}")

        for appletvManager in self.appleTVManagers:
            if int(appletvManager.device_ID) == int(appleTVid):
                self.logger.debug(f"Found correct AppleTV listener/manager. {appletvManager} and id {appletvManager.device_ID}")
                appletvManager.start_app(apptoLaunch)

    def sendRemoteCommand(self, valuesDict, typeId):
        self.logger.debug(f"sendRemoteCommand Called {valuesDict} & {typeId}")
        props = valuesDict.props
        self.logger.debug(f"Props equal: {props}")

        if props["appleTV"] =="" or props["appleTV"]=="":
            self.logger.info("No AppleTV selected.")
            return

        appleTVid = props["appleTV"]
        command = props["command"]
        self.logger.info(f"Sending Command {command} to appleTV Device ID {appleTVid}")

        for appletvManager in self.appleTVManagers:
            if int(appletvManager.device_ID) == int(appleTVid):
                self.logger.debug(f"Found correct AppleTV listener/manager. {appletvManager} and id {appletvManager.device_ID}")
                appletvManager.send_command(command)

    async def process_playstatus(self, playstatus,  atv, time_start,deviceid):
        try:

            #self.logger.debug(f"Process PlayStatus Called {playstatus}, {atv}, {atv.metadata} {time_start} and IndigoDeviceID {deviceid} ")
            self.logger.debug(f"PlayState DEVICE_state {playstatus.device_state}")
            #self.logger.debug(f"PlayState TITLE {playstatus.title}, & Position {playstatus.position} & Artist {playstatus.artist}  & media_type {playstatus.media_type} ")
            #self.logger.debug(f"PlayState TOTAL TIME {playstatus.total_time} & Series Name {playstatus.series_name} && Season_Numer {playstatus.season_number}")
            #self.logger.debug(f"PlayState EpisodeNo {playstatus.episode_number} & Content Identifier {playstatus.content_identifier} ")

            atv_appId = ""
            atv_app = atv.metadata.app
            if atv_app !=None:
                atv_appId = atv.metadata.app.identifier
            self.logger.debug(f"App Playing {atv_appId} and App Name {atv_app}")
            playingState = "Standby"
            if atv is None:
                playingState = "Off"
            elif atv.power.power_state == pyatv.const.PowerState.Off:
                playingState = "Standby"
            state = playstatus.device_state
            if state in (pyatv.const.DeviceState.Idle, pyatv.const.DeviceState.Loading):
                playingState = "Idle"
            if state == pyatv.const.DeviceState.Playing:
                playingState = "Playing"
            if state in (pyatv.const.DeviceState.Paused, pyatv.const.DeviceState.Seeking, pyatv.const.DeviceState.Stopped):
                playingState = "Paused"

            stateList = [
                {'key': 'currentlyPlaying_AppId', 'value': f"{atv_appId}"},
                {'key': 'currentlyPlaying_App', 'value': f"{atv_app}"},
                {'key': 'currentlyPlaying_Artist', 'value': str(playstatus.artist)},
                {'key': 'currentlyPlaying_Album', 'value': str(playstatus.album)},
                {'key': 'currentlyPlaying_DeviceState', 'value': f"{playstatus.device_state}"},
                {'key': 'currentlyPlaying_Genre', 'value': f"{playstatus.genre}"},
                {'key': 'currentlyPlaying_MediaType', 'value': f"{playstatus.media_type}"},
                {'key': 'currentlyPlaying_Position', 'value': f"{playstatus.position}"},
                {'key': 'currentlyPlaying_Repeat', 'value': f"{playstatus.repeat}"},
                {'key': 'currentlyPlaying_Shuffle', 'value': f"{playstatus.shuffle}"},
                {'key': 'currentlyPlaying_Title', 'value': f"{playstatus.title}"},
                {'key': 'currentlyPlaying_TotalTime', 'value': f"{playstatus.total_time}"},
                {'key': 'currentlyPlaying_PlayState', 'value': f"{playingState}"},
            ]
            device = indigo.devices[deviceid]
            device.updateStatesOnServer(stateList)
        except:
            self.logger.exception("process_playlist error")

    async def _async_stop(self):
        while True:
            await asyncio.sleep(1.0)
            if self.stopThread:
                break

    def menu_callback(self, valuesDict, *args, **kwargs):  # typeId, devId):
        self.logger.debug("Subtype callback: returning valuesDict \n {}".format(valuesDict))
        return valuesDict

    def app_list_generator(self, filter="", values_dict=None, typeId="", targetId=0):
        try:
            state_list = []
            self.logger.debug(f"applistgenerator called {values_dict}")
            if "appleTV" in values_dict:
                try:
                    deviceid = values_dict["appleTV"]
                    for appletvManager in self.appleTVManagers:
                        if int(appletvManager.device_ID) == int(deviceid):
                            self.logger.debug(f"Found correct AppleTV listener/manager. {appletvManager} and id {appletvManager.device_ID}")
                            #state_list = list(appletvManager.app_list.items())
                            state_list =  [(v, k) for k, v in appletvManager.app_list.items()]

                except:
                    state_list.append(("invalid", "invalid device type"))

        except:
            self.logger.debug("Caught Exception device State Generator", exc_info=True)

        self.logger.debug(f"State List {state_list}")
        return state_list




    async def return_MatchedappleTVs(self, identifier):
        self.logger.debug("Returning all ATVS")
        atvs = await pyatv.scan(self._event_loop)
        if not atvs:
            self.logger.info("No devices found")
            return None
        else:
            self.logger.debug(f"atvs {atvs}")
            for atv in atvs:
                self.logger.debug(f"Device Identifer: {identifier}  && appleTV {atv.identifier}")
                if identifier == str(atv.identifier):
                    self.logger.debug(f"Found Matching Device {atv.identifier}, start Pairing.")
                    self._event_loop.create_task(self.one_pairing(atv))
                    return
    ########################################
    # Relay / Dimmer Action callback
    ######################
    def actionControlDevice(self, action, dev):
        for appletvManager in self.appleTVManagers:
            if int(appletvManager.device_ID) == int(dev.id):
                self.logger.debug(f"Found correct AppleTV listener/manager. {appletvManager} and id {appletvManager.device_ID}")

                if action.deviceAction == indigo.kDeviceAction.TurnOn:
                    command = "turn_on"
                    appletvManager.power_on()

                elif action.deviceAction == indigo.kDeviceAction.TurnOff:
                    command = "turn_off"
                    appletvManager.power_off()

                elif action.deviceAction == indigo.kDeviceAction.Toggle:
                    # Command hardware module (dev) to toggle here:
                    # ** IMPLEMENT ME **
                    new_on_state = not dev.onState
                    if new_on_state:
                        command = "turn_on"
                        appletvManager.power_on()
                    else:
                        command = "turn_off"
                        appletvManager.power_off()

                self.sleep(0.1)
                powerstate = appletvManager.power
                self.logger.debug(f"Curent powerstate == {powerstate}")





    ########################################
    # General Action callback
    ######################
    def actionControlUniversal(self, action, dev):
        ###### BEEP ######
        if action.deviceAction == indigo.kUniversalAction.Beep:
            # Beep the hardware module (dev) here:
            # ** IMPLEMENT ME **
            self.logger.info(f"sent \"{dev.name}\" beep request")

        ###### ENERGY UPDATE ######
        elif action.deviceAction == indigo.kUniversalAction.EnergyUpdate:
            # Request hardware module (dev) for its most recent meter data here:
            # ** IMPLEMENT ME **
            self.logger.info(f"sent \"{dev.name}\" energy update request")

        ###### ENERGY RESET ######
        elif action.deviceAction == indigo.kUniversalAction.EnergyReset:
            # Request that the hardware module (dev) reset its accumulative energy usage data here:
            # ** IMPLEMENT ME **
            self.logger.info(f"sent \"{dev.name}\" energy reset request")

        ###### STATUS REQUEST ######
        elif action.deviceAction == indigo.kUniversalAction.RequestStatus:
            # Query hardware module (dev) for its current status here:
            # ** IMPLEMENT ME **
            self.logger.info(f"sent \"{dev.name}\" status request")

    ########################################

    async def get_appleTVs(self):
        """Find a device and print what is playing."""
        try:
            self.logger.info("Discovering appleTV devices on network...")
            atvs = await pyatv.scan(self._event_loop)
            if not atvs:
                self.logger.info("No device found")
                return None
            else:
                self.logger.debug(f"atvs {atvs}")
                #output = "\n\n".join(str(result) for result in atvs)
                #self.logger.info(f"{output}")
                for atv in atvs:
                    self.createNewDevice(atv)

        except:
            self.logger.exception("Exception in get appleTVs")

    def createNewDevice(self, atv):

        ip = str(atv.address)
        name = atv.name
        operating_system = atv.device_info.operating_system.TvOS
        mac = atv.device_info.mac
        model = atv.device_info.model
        identifier = atv.identifier

        self.logger.debug(f"\n{ip}\n{name}\n{mac}\n{model}\n{operating_system}")

        for dev in indigo.devices.iter("self"):
            if "identifier" not in dev.states: continue
            if str(dev.states["identifier"]) == str(identifier):
                self.logger.debug(f"Found exisiting device same Identifier. Skipping: {dev.name}")
                return

        if operating_system == atv.device_info.operating_system.TvOS:
            devProps = {}
            devProps[u"isAppleTV"] = True
            devProps[u"SupportsOnState"] = False
            devProps[u"SupportsSensorValue"] = False
            devProps[u"SupportsStatusRequest"] = False
            devProps[u"AllowOnStateChange"] = False
            devProps[u"AllowSensorValueChange"] = False
            devProps[u"IP"] = str(ip)
            devProps[u"MAC"] = str(mac)
            devProps["Name"] = str(name)
            devProps["Model"] = str(model)
            devProps["Identifier"] = str(identifier)
            stateList = [
                {'key': 'ip', 'value': ip},
                {'key': 'MAC', 'value': str(mac)},
                {'key': 'name', 'value': str(name)},
                {'key': 'model', 'value': str(model)},
                {'key': 'identifier', 'value': str(identifier)},
            ]
            self.logger.debug(f"Statelist \n {stateList}")
            dev = indigo.device.create(
                protocol=		indigo.kProtocol.Plugin,
                address =		 ip,
                name =			 "appleTV " + name,
                description =	 name,
                pluginId =		 self.pluginId,
                deviceTypeId =	 "appleTV",
                props =			 devProps)

            dev.updateStatesOnServer(stateList)
            self.sleep(1)
            self.logger.info(f"AppleTV Indigo plugin Device Created:  {dev.name}")

