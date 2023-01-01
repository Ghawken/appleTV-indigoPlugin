#! /usr/bin/env python3.10
# -*- coding: utf-8 -*-

"""
Author: GlennNZ

"""
import logging
import threading

import traceback
import inspect
import asyncio
from packaging import version
import ipaddress

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
import binascii

try:
    import pyatv
    import pyatv.const
    from pyatv.const import (
        FeatureName,
        FeatureState,
        InputAction,
        Protocol,
        RepeatState,
        ShuffleState,
        PairingRequirement
    )
    import pyatv.exceptions
    from pyatv.interface import retrieve_commands
except:
    # error in init when can message
    pass

import subprocess
import sys
import os
from os import path


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
# class IndigoFileLogHandler(TimedRotatingFileHandler):
#     def emit(self, record, **kwargs):
#         try:
#             levelno = int(record.levelno)
#             if self.level <= levelno:  ## Don't do anything if level display is lower
#                 new_msg = f"{path.basename(record.pathname)}:{record.funcName}:{record.lineno}"
#                 try:
#                     second_msg = record.msg % record.args
#                 except:
#                     second_msg = record.msg
#                 record.msg =  str(new_msg+" : "+second_msg)
#                 record.args = None  ## This is the old string formatting %s issue.  Need to combine and then delete all args
#                 try:
#                     if self.shouldRollover(record):
#                         self.doRollover()
#                     logging.FileHandler.emit(self, record)
#                 except Exception:
#                     self.handleError(record)
#
#         except Exception as ex:
#             indigo.server.log(f"Error in Loggging FileHandler: {ex}")
#             indigo.server.log(f"Error in Logging FileHandler execution:\n\n{traceback.format_exc(30)}", isError=False)
#             pass
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

    def __init__(self, plugin, loop, atv_config,deviceid, config_appleTV, thisisHomePod, devicename):
        self.plugin = plugin
        self.plugin.logger.debug("Within init of AppleTVListener/all")
        self.deviceid = deviceid
        self.atv = None
        #self.isAppleTV = config_appleTV
        self.isAppleTV = None ## generate this internally in this service
        self.isHomePod = thisisHomePod
        self.loop = loop
        self.atv_config = atv_config
        self.devicename = devicename
        self._app_list = None
        self.all_features = None
        self.cast = "unicast"
        self._killConnection = False
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

    @property
    def list_features(self):
        """Print a list of all features and options."""
        try:
            all_features = self.atv.features.all_features(include_unsupported=False)
            str_return = f"\n{self.devicename}\nFeature list:\n---------------- \n"

            for name, feature in all_features.items():
                str_return +=  f"{name.name}: {feature.state.name}\n"
                options = [f"{k}={v}" for k, v in feature.options.items()]
                if options:
                    str_return += f", Options={', '.join(options)}\n"

            str_return += "\nLegend:\n"
            str_return += "-------\n"
            str_return +="Available: Supported by device and usable now\n"
            str_return +="Unavailable: Supported by device but not usable now\n"
            str_return +="Unknown: Supported by the device but availability not known\n"
            str_return +="Unsupported: Not supported by this device (or by pyatv)\n"
            return str_return
        except:
            self.plugin.logger.exception("list_features error:")

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
                self.plugin.logger.debug("Listing apps is not supported", exc_info=True)
            except pyatv.exceptions.ProtocolError:
                self.plugin.logger.debug("Failed to update app list", exc_info=True)
            else:
                self._app_list = {
                    app.name: app.identifier
                    for app in sorted(apps, key=lambda app: app.name.lower())
                }
                self.plugin.logger.debug(f"{self._app_list}")
        except pyatv.exceptions.NotSupportedError:
            self.plugin.logger.info("App Listing not supported on this device")
            self._app_list = {}
            return
        except:
            self.plugin.logger.debug("Update App list issue", exc_info=True)

    def power_on(self):
        if self.atv !=None:
            self.plugin.logger.debug(f"send atc.power turn on command")
            self.loop.create_task(self.atv.power.turn_on())

    def power_off(self):
        if self.atv !=None:
            self.plugin.logger.debug(f"send atc.power turn off command")
            self.loop.create_task(self.atv.power.turn_off())


    def powerstate_update( self, old_state, new_state  ):
        try:
            self.plugin.logger.debug(f"{self.devicename} Powerstate update Old {old_state} and new {new_state}")
            device = indigo.devices[self.deviceid]
            if new_state == pyatv.const.PowerState.On:
                device.updateStateOnServer("onOffState", True)
                device.updateStateOnServer("PowerState","On")
                device.updateStateImageOnServer(indigo.kStateImageSel.PowerOn)
            elif new_state == pyatv.const.PowerState.Off:
                device.updateStateOnServer("onOffState", False)
                device.updateStateOnServer("PowerState", "Idle")
                device.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
        except:
            self.plugin.logger.debug("Exception in Powerstate Updatee",exc_info=True)


    def _handle_disconnect(self):
        """Handle that the device disconnected and restart connect loop."""
        try:
            if self.atv:
                self.atv.close()
                self.atv = None
            if self._task:
                self._task.cancel()
                self._task = None

            self._task = self.loop.create_task(self.loop_atv(self.loop, atv_config=self.atv_config, deviceid=self.deviceid))
        except:
            self.plugin.logger.debugf("_handle disconnect and restart", exc_info=True)

    def disconnect(self):
        """Disconnect from device."""
        self.plugin.logger.debug(f"Disconnecting from device {self.devicename}")
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
        try:
            self.plugin.logger.info(f"Connection to appleTV - {self.devicename} lost.")
            self._killConnection = True
        except:
            self.plugin.logger.exception("Connection Lost Exception")

    def connection_closed(self) -> None:
        """Call when connection was closed."""
        self.plugin.logger.info(f"Connection to appleTV - {self.devicename} closed.")
        self._killConnection = True

    def playstatus_update(self, updater, playstatus: pyatv.interface.Playing) -> None:
        """Call when play status was updated."""
        try:
            self.plugin.logger.debug(f"Playstatus Update Called for {self.devicename}")
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
                    self.deviceid,
                    self.isAppleTV
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

#### redo Remote control handling - programmatically generate menu items

    def _typeparse(self, value):
        try:
            return int(value)
        except ValueError:
            return value

    def _parse_args(self, cmd, args):
        args = [self._typeparse(x) for x in args]
        if cmd == "set_shuffle":
            return [ShuffleState(args[0])]
        if cmd == "set_repeat":
            return [RepeatState(args[0])]
        if cmd in ["up", "down", "left", "right", "select", "menu", "home"]:
            return [InputAction(args[0])]
        if cmd == "set_volume":
            return [float(args[0])]
        return args

    def _extract_command_with_args(self, cmd):
        """Parse input command with arguments.
        Parses the input command in such a way that the user may
        provide additional argument to the command. The format used is this:
          command=arg1,arg2,arg3,...
        all the additional arguments are passed as arguments to the target
        method.
        """
        equal_sign = cmd.find("=")
        if equal_sign == -1:
            return cmd, []

        command = cmd[0:equal_sign]
        args = cmd[equal_sign + 1:].split(",")
        return command, self._parse_args(command, args)

    async def async_artwork_save(self, filename, width=None, height=None):
        """Download artwork and save it to artwork.png."""
        try:
            artwork = await self.atv.metadata.artwork(width=width, height=height)
            if artwork is not None:
                with open(filename, "wb") as file:
                    file.write(artwork.bytes)
                    self.plugin.logger.debug(f"Artwork Downloaded , mimetype {artwork.mimetype}")
            else:
                self.plugin.logger.info("No artwork is currently available.")
        except:
            self.plugin.logger.exception("async artwork save exception")

    async def _handle_device_command(self, args, cmd ):
        try:
           # device = retrieve_commands(pyatv.DeviceCommands)
            self.plugin.logger.debug(f"_handle_device_command called - Args: {args}  Cmd:{cmd}")
            if self.atv == None:
                self.plugin.logger.info("Current AppleTV is not connected.  Aborting Command request.")
                return
            ctrl = retrieve_commands(pyatv.interface.RemoteControl)
            metadata = retrieve_commands(pyatv.interface.Metadata)
            power = retrieve_commands(pyatv.interface.Power)
            playing = retrieve_commands(pyatv.interface.Playing)
            stream = retrieve_commands(pyatv.interface.Stream)
            device_info = retrieve_commands(pyatv.interface.DeviceInfo)
            apps = retrieve_commands(pyatv.interface.Apps)
            audio = retrieve_commands(pyatv.interface.Audio)
            # Parse input command and argument from user
            cmd, cmd_args = self._extract_command_with_args(cmd)
           # cmd, cmd_args = cmd, self._parse_args(cmd, args)

            self.plugin.logger.debug(f"cmd and cmd_args extracted and Cmd {cmd} and cmd_args {cmd_args}")
            # if cmd in device:
            #     return await _exec_command(
            #         DeviceCommands(atv, loop, args), cmd, False, *cmd_args
            #     )
            # NB: Needs to be above RemoteControl for now as volume_up/down exists in both
            # but implementations in Audio shall be called
            if cmd in audio:
                return await self._exec_command(self.atv.audio, cmd, True, *cmd_args)

            if cmd in ctrl:
                return await self._exec_command(self.atv.remote_control, cmd, True, *cmd_args)

            if cmd in metadata:
                return await self._exec_command(self.atv.metadata, cmd, True, *cmd_args)

            if cmd in power:
                return await self._exec_command(self.atv.power, cmd, True, *cmd_args)

            if cmd in playing:
                playing_resp = await self.atv.metadata.playing()
                return await self._exec_command(playing_resp, cmd, True, *cmd_args)

            if cmd in stream:
                return await self._exec_command(self.atv.stream, cmd, True, *cmd_args)

            if cmd in device_info:
                return await self._exec_command(self.atv.device_info, cmd, True, *cmd_args)

            if cmd in apps:
                return await self._exec_command(self.atv.apps, cmd, True, *cmd_args)

            self.plugin.logger.error(f"Unknown command: {cmd}")
            return 1
        except:
            self.plugin.logger.exception("")

    async def _exec_command(self, obj, command, print_result, *args):
        try:

            # If the command to execute is a @property, the value returned by that
            # property will be stored in tmp. Otherwise it's a coroutine and we
            # have to yield for the result and wait until it is available.
            tmp = getattr(obj, command)
            if inspect.ismethod(tmp):
                # Special case for stream_file: if - is passed as input file, use stdin
                # as source instead of passing filename
                if command == pyatv.interface.Stream.stream_file.__name__ and args[0] == "-":
                    args = [sys.stdin.buffer, *args[1:]]
                value = await tmp(*args)
            else:
                value = tmp

            # Some commands might produce output themselves (especially non-API
            # commands), so don't print the return code they might give
            if print_result:
                self._pretty_print(value)
                return 0
            return value

        except NotImplementedError:
            self.plugin.logger.info(f"Command {command} is not supported by device")
        except pyatv.exceptions.AuthenticationError as ex:
            self.plugin.logger.info(f"Authentication error: {ex}")
            self.plugin.logger.debug(f"Authentication error: {ex}", exc_info=True)
        except TypeError:
            self.plugin.logger.info(f"Run Command {command} Failed with a 'TypeError'.  Normally this means you have specified Optional Arguments for a command that should have none. ")
            self.plugin.logger.info(f"Please check and delete Optional Arguments in the action.")
            self.plugin.logger.debug(f"Type Error caught.  ?Optional Arguments.  Full Error:",exc_info=True)
        except:
            self.plugin.logger.debug("General Exception Caught:",exc_info=True)
            self.plugin.logger.info("Could not run this command at this time.")
        return 1

    def _pretty_print(self, data):
        if data is None:
            return
        if isinstance(data, bytes):
            self.plugin.logger.info(binascii.hexlify(data))
        elif isinstance(data, list):
            self.plugin.logger.info(", ".join([str(item) for item in data]))
        else:
            self.plugin.logger.info(data)


    def send_command(self, command, args,  **kwargs):
        try:
            self.plugin.logger.debug(f"Within send_command and command & args - {command} and args {args}")
            self.loop.create_task(self._handle_device_command(args, command))
        except:
            self.plugin.logger.exception("Error in send_command")

    def save_artwork(self, filename, width, heigth,  **kwargs):
        try:
            self.plugin.logger.debug(f"Within Save Artwork Filename: {filename}, width {width}")
            self.loop.create_task(self.async_artwork_save(filename, width, None))
        except:
            self.plugin.logger.exception("Error in save_Artwork")

    def playstatus_error(self, updater, exception: Exception) -> None:
        self.plugin.logger.debug("Error in Playstatus", exc_info=True)


    async def connect_atv(self, loop, identifier, airplay_credentials, ipaddress, cast):
        """Find a device and print what is playing."""
        try:
            if cast == "unicast":
                self.plugin.logger.info(f"Scanning for device using IP address: {ipaddress} and using Unicast.")
                atvs = await pyatv.scan(loop, identifier=identifier, hosts=[ipaddress], timeout=15)
            else:
                self.plugin.logger.info(f"Scanning for device using Multicast.")
                atvs = await pyatv.scan(loop, identifier=identifier, timeout=20)
            if not atvs:
                self.plugin.logger.info(f"Failed connection as this specific {self.devicename} cannot be found.  Please check its network connection.")
                return (False,"")

            config = atvs[0]
            self.plugin.logger.debug(f"AppleTV:\n {config}") #{config.services[0].pairing}")
            self.isAppleTV = False
            for service in config.services:
                if service.pairing == PairingRequirement.NotNeeded or service.pairing == PairingRequirement.Disabled or service.pairing == PairingRequirement.Unsupported:
                    self.plugin.logger.debug(f"\nService Protocol SKIPPED: {service.protocol}\nServicePort:{service.port}\nServiceEnabled:{service.enabled}\nServiceProperties:{service.properties}\nServicePairing:{service.pairing}\nServiceIdent:{service.identifier}")
                    continue
                else:
                    self.plugin.logger.debug(f"\nService Protocol: {service.protocol}\nServicePort:{service.port}\nServiceEnabled:{service.enabled}\nServiceProperties:{service.properties}\nServicePairing:{service.pairing}\nServiceIdent:{service.identifier}")
                    if service.enabled:
                        config.set_credentials(service.protocol, airplay_credentials)
                        self.plugin.logger.debug(f"Set Credentials {airplay_credentials} for service {service.protocol}")
                        self.isAppleTV = True   ## if credentials == then become appleTV - not correct Samsung TV...
                    else:
                        if service.protocol == pyatv.Protocol.MRP:
                            self.plugin.logger.info(f"{self.devicename} has MRP Protocol disabled on this device.  This will impact PowerState reporting.")
                        else:
                            self.plugin.logger.info(f"{self.devicename} has Protocol: {service.protocol} disabled.  This may impact functionality")

            self.plugin.logger.debug(f"Connecting to {config.address}")
            return (await pyatv.connect(config, loop), config.address)
        except:
            self.plugin.logger.exception("Connect ATV Exception")
            return (False, "")

    def validate_ip_address(self, address):
        try:
            ip = ipaddress.ip_address(address)
            self.plugin.logger.debug(f"IP address {address} is valid. The object returned is {ip}")
            return True
        except ValueError:
            self.plugin.logger.debug(f"IP address {address} is not valid")
            return False

    async def loop_atv(self, loop, atv_config, deviceid):
        timeretry = 10
        retries = 0
        while True:
            if timeretry > 600:
                timeretry = 60
            device = indigo.devices[deviceid]
            ipaddress = device.states["ip"]
            try:
                identifier = atv_config["identifier"]
                airplay_credentials = atv_config["credentials"]
                if self.validate_ip_address(ipaddress) and self.cast == "unicast":  ## startup
                    (self.atv, newipaddress) = await self.connect_atv(loop, identifier, airplay_credentials, ipaddress, self.cast)
                else:  ## if anything other than unicast or invalid IP use multicast
                    (self.atv, newipaddress) = await self.connect_atv(loop, identifier, airplay_credentials, "", self.cast)
                if self.atv:
                    self.atv.listener = self
                    self.atv.push_updater.listener = self
                    self.atv.push_updater.start()
                    self.atv.power.listener =self
                    self.plugin.logger.debug("Push updater started")
                    device = indigo.devices[deviceid]
                    device.updateStateOnServer(key="status", value="Paired. Push Updating.")
                    self.plugin.logger.debug(f"New IP ADDRESS: {newipaddress}")
                    #localPropsCopy = device.ownerProps
                    #localPropsCopy["IP"] = "this is my IP:"+str(newipaddress)
                    #device.replacePluginPropsOnServer(localPropsCopy)
                    if str(ipaddress) != str(newipaddress):
                        if self.validate_ip_address(newipaddress):
                            device.updateStateOnServer(key="ip", value=str(newipaddress))
                            localPropsCopy = device.ownerProps
                            localPropsCopy["IP"] = str(newipaddress)
                            device.replacePluginPropsOnServer(localPropsCopy)
                            self.plugin.logger.info(f"AppleTV IP Address has changed, updating Indigo Device.  Using new IP {newipaddress}")
                    # Update app list
                    self.plugin.logger.debug("Updating app list")
                    self.plugin.logger.info(f"{device.name} successfully connected and real-time Push updating enabled. (if available!)")
                    timeretry = 10
                    if self.isAppleTV:
                        try:
                            await self._update_app_list()
                        except pyatv.exceptions.NotSupportedError:
                            pass
                    while True:
                        await asyncio.sleep(20)
                        self.plugin.logger.debug(f"Within main sleep 20 second loop killconnection {self._killConnection}")
                        if self._killConnection:
                            self.plugin.logger.debug("Manually raise ConnectionReset Error - Kill Current Connection")
                            raise ConnectionResetError("Connection lost.  Raising Exception to restart loop manually.")
                else:
                    await asyncio.sleep(timeretry)
                    self.plugin.logger.debug(f"Attempting to Connect again...and self._killconnection {self._killConnection}")
                    timeretry = timeretry + 10
                    retries = retries + 1
                    if retries>=3:
                        self.plugin.logger.debug("Changing to Multicast Discovery as unicast IP based has failed.")
                        if self.cast == "unicast":
                            self.cast="multicast"
                        else:
                            self.cast=="unicast"
                        ### go from one to another in sets of 3...
                        retries = 0

            except ConnectionResetError:
                self.plugin.logger.debug(f"Connection lost, ended or otherwise.  Hopefully restarting loop", exc_info=True)
                self._killConnection = False
            except Exception:
                self.plugin.logger.debug("Exception in Loop_ATV:  Should restart.",exc_info=True)
    ################################################################################

class Plugin(indigo.PluginBase):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        pfmt = logging.Formatter('%(asctime)s.%(msecs)03d\t%(levelname)s\t%(name)s.%(funcName)s:%(filename)s:%(lineno)s:\t%(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        self.plugin_file_handler.setFormatter(pfmt)
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
        self.previousVersion = self.pluginPrefs.get("previousVersion", "0.0.1")
        self.indigo_log_handler = IndigoLogHandler(pluginDisplayName, logging.INFO)
        ifmt = logging.Formatter("%(message)s")
        self.indigo_log_handler.setFormatter(ifmt)
        self.indigo_log_handler.setLevel(self.logLevel)
        self.logger.addHandler(self.indigo_log_handler)
        self.forceAllDiscovery = False
        self.pathtoPlugin = os.getcwd()
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

        self.debug1 = self.pluginPrefs.get('debug1', False)
        self.debug2 = self.pluginPrefs.get('debug2', False)
        self.debug3 = self.pluginPrefs.get('debug3', False)
        self.debug4 = self.pluginPrefs.get('debug4', False)
        self.debug5 = self.pluginPrefs.get('debug5', False)
        self.debug6 = self.pluginPrefs.get('debug6', False)
        self.debug7 = self.pluginPrefs.get('debug7', False)
        self.debug8 = self.pluginPrefs.get('debug8', False)
        self.debug9 = self.pluginPrefs.get('debug9', False)

        self._event_loop = None
        self._another_event_loop = None
        self._async_thread = None

        if self.debug1:
            pyatv_logging = logging.getLogger("pyatv")
            pyatv_logging.setLevel(logging.THREADDEBUG)
            #pyatv_logging.addHandler(self.indigo_log_handler)
            pyatv_logging.addHandler(self.plugin_file_handler)
        else:
            pyatv_logging = logging.getLogger("pyatv")
            pyatv_logging.setLevel(logging.INFO)
            pyatv_logging.addHandler(self.plugin_file_handler)

        MAChome = os.path.expanduser("~") + "/"
        self.saveDirectory = MAChome + "Documents/Indigo-appleTV/"

        self.logger.info(u"{0:=^130}".format(" End Initializing New Plugin  "))
        try:
            if version.parse(pluginVersion) != version.parse(self.previousVersion):
                self.logger.info("Plugin Updated Version Detected.  Please run xattr command as below (copy & paste to terminal)")
                self.logger.info("This enables Say Annoucements on HomePods.  If unused, then will not affect other functioning.")
                self.logger.info("{}".format("sudo xattr -rd com.apple.quarantine '" + indigo.server.getInstallFolderPath() + "/" + "Plugins'"))
                self.logger.info(u"{0:=^130}".format(" End of Setup "))
                self.pluginPrefs['previousVersion']= pluginVersion
        except:
            pass


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

            self.forceAllDiscovery = valuesDict.get('forceDiscovery', False)

            if self.debug3:
                logging.getLogger("Plugin.HomeKit_pyHap").setLevel(logging.DEBUG)
            else:
                logging.getLogger("Plugin.HomeKit_pyHap").setLevel(logging.INFO)

            self.logger.debug(u"logLevel = " + str(self.logLevel))
            self.logger.debug(u"User prefs saved.")
            self.logger.debug(u"Debugging on (Level: {0})".format(self.logLevel))
            if self.debug1:
                pyatv_logging = logging.getLogger("pyatv")
                pyatv_logging.setLevel(logging.THREADDEBUG)
                # pyatv_logging.addHandler(self.indigo_log_handler)
                pyatv_logging.addHandler(self.plugin_file_handler)
            else:
                pyatv_logging = logging.getLogger("pyatv")
                pyatv_logging.setLevel(logging.INFO)
                pyatv_logging.addHandler(self.plugin_file_handler)

        return True

    def deviceStartComm(self, device):
        self.logger.debug(f"{device.name}: Starting {device.deviceTypeId} Device {device.id} ")
        device.stateListOrDisplayStateIdChanged()

        if device.enabled:
            device.updateStateOnServer(key="status", value="Starting Up")
            device.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
            identifier = device.states["identifier"]
            credentials = device.ownerProps.get("credentials","")
            if credentials != "" :
                self.logger.info(f"{device.name} Device has been Setup, attempting to connect.")
                new_data = {}
                if credentials == "":  ## future use.
                    thisisappleTV = False
                else:
                    thisisappleTV = True
                new_data["credentials"] = credentials
                new_data["identifier"] = identifier
                self.appleTVManagers.append( appleTVListener(self, self._event_loop, new_data, device.id, thisisappleTV, False, device.name ))
            else:
                self.logger.info(f"{device.name} has not been setup in Device Edit.  Suggest setup connection or delete device.")
                device.updateStateOnServer(key="status", value="Awaiting Setup")
                device.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
        else:
            device.updateStateOnServer(key="status", value="Starting Up")
            device.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)


    def startPairing(self, valuesDict, type_id="", dev_id=None):
        self.logger.debug(u'Start Pairing Button pressed Called.')
       # self.logger.debug(f"valueDict {valuesDict}\n, type_id {type_id}, and dev_id {dev_id}")
        self._appleTVpairing  = None
        device = indigo.devices[dev_id]
        devicename = device.name
        identifier = device.states['identifier']
        ipaddress = device.states['ip']
        if self.validate_ip_address(ipaddress):
        # get all atvs
            self._event_loop.create_task(self.return_MatchedappleTVs(identifier, devicename, ipaddress))
        else:
            self._event_loop.create_task(self.return_MatchedappleTVs(identifier, devicename, "UNKNOWN"))
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
            return

    async def one_pairing(self, atv, devicename):
        try:
            self.logger.debug(f"First Step One Pairing Started {atv.identifier} & Indigo Device {devicename}")
            service = atv.get_service(pyatv.Protocol.AirPlay)
            self.logger.debug(f"Service: {service}")
            if service.pairing == PairingRequirement.Unsupported:
                self.logger.debug(f"{pyatv.Protocol.AirPlay} does not support pairing")
                self._paired_credentials = "Pairing is Unsupported"
                self.logger.info(f"{devicename} does not need Pairing.  I will attempt to Connect.  Press Save to continue.")
                return "Pairing is Unsupported"
            elif service.pairing == PairingRequirement.Disabled:
                self.logger.debug(f"{pyatv.Protocol.AirPlay} does not support pairing. Disabled.")

                self.logger.info(f"{devicename} does not need Pairing.  Attempt to Connect.  Press Save to continue.")
                self._paired_credentials = "Pairing is Disabled"
                return "Pairing is Disabled"
            elif service.pairing == PairingRequirement.NotNeeded:
                self.logger.debug(f"{pyatv.Protocol.AirPlay} does not support pairing. Not Needed.")
                self.logger.info(f"{devicename} does not need Pairing.  Attempt to Connect.  Press Save to continue.")
                self._paired_credentials = "Pairing is Not Needed"
                return "Pairing is Not Needed"
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
        #valuesDict['credentials'] = credentials

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

    ##
    def menu_actionRun(self, valuesDict, typeId):
        self.logger.debug(f"Running Logging Command {valuesDict}")
        try:
            appleTV = int(valuesDict["appleTV"])  ## deviceID
            action = str(valuesDict["option"])
            something_done = False
            deviceid = appleTV
            device = indigo.devices[deviceid]

            if action=="scandevice":
                identifier = device.states['identifier']
                self._event_loop.create_task(self.menu_logatvc(iden=identifier))
                return
            elif action == "showcommands":
                foundDevice = False
                for appletvManager in self.appleTVManagers:  ## will only show running devices.
                    if int(appletvManager.device_ID) == int(deviceid):
                        foundDevice = True
                        self.logger.debug(f"Found correct AppleTV listener/manager. {appletvManager} and id {appletvManager.device_ID}")
                        self._print_commands("\nRemote control", pyatv.interface.RemoteControl)
                        self._print_commands("\nMetadata", pyatv.interface.Metadata)
                        self._print_commands("\nPower", pyatv.interface.Power)
                        self._print_commands("\nPlaying", pyatv.interface.Playing)
                        self._print_commands("\nAirPlay", pyatv.interface.Stream)
                        self._print_commands("\nDevice Info", pyatv.interface.DeviceInfo)
                        self._print_commands("\nAudio", pyatv.interface.Audio)
                        self._print_commands("\nApps", pyatv.interface.Apps)

                        ##
                        #self.logger.error(f" Commands: \n {retrieve_commands(pyatv.interface.RemoteControl)}")

                        return
                if foundDevice == False:
                    self.logger.info("Device must be Paired and connected for this to function")
                    return
            elif action == "showFeatures":
                foundDevice = False
                for appletvManager in self.appleTVManagers:  ## will only show running devices.
                    if int(appletvManager.device_ID) == int(deviceid):
                        result = appletvManager.list_features
                        self.logger.info(f"{result}")
                        return
                if foundDevice == False:
                    self.logger.info("Device must be Paired and connected for this to function")
                    return

        except:
            self.logger.exception("Caught exception in actionRun")
#########################################################################

    def _print_commands(self, title, api):
        cmd_list = retrieve_commands(api)
        commands = " - " + "\n - ".join(
            map(lambda x: x[0] + " - " + x[1], sorted(cmd_list.items()))
        )
        self.logger.info(f"{title} commands:\n{commands}\n")

#####################################################################


#####################################################################

    async def menu_logatvc(self, iden):
        """Find a device and print what is playing."""
        try:
            self.logger.info("Discovering appleTV devices on network...")
            atvs = await pyatv.scan(self._event_loop, identifier=iden)
            if not atvs:
                self.logger.info(f"This device idenity {iden} could no longer be found.")
                return None
            else:
                self.logger.debug(f"atvs {atvs}")
                output = "\n\n".join(str(result) for result in atvs)
                self.logger.info(u"\n{0:=^165}".format(" Device: Iden: "+str(iden)))
                self.logger.info(f"\n {output} \n")
                self.logger.info(u"{0:=^165}".format(" End of Data "))
        except:
            self.logger.exception("Exception in get menu_log_atvs")

#######################################################################
    def didDeviceCommPropertyChange(self, origDev, newDev):
        # example of customizing the call:
        if origDev.pluginProps.get('credentials', '') != newDev.pluginProps.get('credentials', ''):
            return True
        return super(Plugin, self).didDeviceCommPropertyChange(origDev, newDev)


    def validateDeviceConfigUi(self, values_dict, type_id, dev_id):
        try:
            self.logger.debug(f"ValidateDevice Config UI called {values_dict} and ID {dev_id}")
            self.sleep(0.2)
            if self._paired_credentials != None:
                values_dict["credentials"]= str(self._paired_credentials)
                values_dict["isPaired"] = True
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

        MAChome = os.path.expanduser("~") + "/"
        self.saveDirectory = MAChome + "Pictures/Indigo-appleTV/"

        self.speakPath = os.path.join(self.pluginprefDirectory, "speak")

        try:

            if not os.path.exists(self.pluginprefDirectory):
                os.makedirs(self.pluginprefDirectory)
            if not os.path.exists(self.saveDirectory):
                os.makedirs(self.saveDirectory)
            speakpath = os.path.join(self.pluginprefDirectory, "speak")
            if not os.path.exists(self.speakPath):
                os.makedirs(self.speakPath)

        except:
            self.logger.error(u'Error Accessing Save and Peak Directory. ')
            pass


    def shutdown(self):
        self.logger.info("Shutting down Plugin")


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
        forceDiscovery = values_dict["forceDiscovery"]
        scanIPaddress = values_dict.get("scanIPaddress", False)
        IPaddress = values_dict.get("IPaddress", "")

        if scanIPaddress:
            if IPaddress !="" and self.validate_ip_address(IPaddress):
                self._event_loop.create_task(self.get_appleTVs_IP(forceDiscovery, hosts=IPaddress))
            else:
                self.logger.info("Invalid IP Address, please correct or unselect scan single IP address")
                return
        else:
            self._event_loop.create_task(self.get_appleTVs(forceDiscovery))

    def validate_ip_address(self, address):
        try:
            ip = ipaddress.ip_address(address)
            self.logger.debug(f"IP address {address} is valid. The object returned is {ip}")
            return True
        except ValueError:
            self.logger.debug(f"IP address {address} is not valid")
            return False

    def commandListGenerator(self, filter="", values_dict=None, typeId="", targetId=0):
        try:
            state_list = []
            cmd_list = {}
            pwr_list = {}
            meta_list = {}
            play_list = {}
            stream_list = {}
            audio_list = {}
            app_list = {}

            self.logger.debug(f"commandListGenerator called {values_dict}")
            if "appleTV" in values_dict:
                try:
                    deviceid = values_dict["appleTV"]

                    for appletvManager in self.appleTVManagers:
                        if int(appletvManager.device_ID) == int(deviceid):
                            self.logger.debug(f"Found correct AppleTV listener/manager. {appletvManager} and id {appletvManager.device_ID}")
                            try:
                                cmd_list = retrieve_commands( pyatv.interface.RemoteControl)
                            except:
                                self.logger.exception("cmd_list exception")
                                pass
                            try:
                                pwr_list = retrieve_commands(pyatv.interface.Power)
                            except:
                                self.logger.exception("cmd_list exception")
                                pass
                            try:
                                meta_list = retrieve_commands( pyatv.interface.Metadata)
                            except:
                                self.logger.exception("cmd_list exception")
                                pass
                            try:
                                play_list = retrieve_commands(pyatv.interface.Playing)
                            except:
                                self.logger.exception("cmd_list exception")
                                pass
                            try:
                                stream_list = retrieve_commands(pyatv.interface.Stream)
                            except:
                                self.logger.exception("cmd_list exception")
                                pass

                            #info_list = retrieve_commands(pyatv.interface.DeviceInfo)
                            try:
                                audio_list = retrieve_commands(pyatv.interface.Audio)
                            except:
                                self.logger.exception("cmd_list exception")
                                pass
                            try:
                                app_list = retrieve_commands(pyatv.interface.Apps)
                            except:
                                self.logger.exception("cmd_list exception")
                                pass
                            self.logger.debug(f"cmd_list {cmd_list}")
                            state_list.append((-1, "%%disabled:Remote Commands:%%"))
                            for key,value in cmd_list.items():
                                if not "DEPRECATED" in value:
                                    state_list.append((key,value))
                            state_list.append((-1, "%%disabled:Power Commands:%%"))
                            for key,value in pwr_list.items():
                                if not "DEPRECATED" in value:
                                    state_list.append((key,value))
                            state_list.append((-1, "%%disabled:Playing Commands:%%"))
                            for key, value in play_list.items():
                                if not "DEPRECATED" in value:
                                    state_list.append((key, value))
                            state_list.append((-1, "%%disabled:Audio Commands:%%"))
                            for key, value in audio_list.items():
                                if not "DEPRECATED" in value:
                                    state_list.append((key, key))  ##description
                            state_list.append((-1, "%%disabled:MetaData Commands:%%"))
                            for key, value in meta_list.items():
                                if not "DEPRECATED" in value:
                                    state_list.append((key, value))
                            state_list.append((-1, "%%disabled:Streaming Commands:%%"))
                            for key, value in stream_list.items():
                                if not "DEPRECATED" in value:
                                    state_list.append((key, value))
                            state_list.append((-1, "%%disabled:App Commands:%%"))
                            for key, value in app_list.items():
                                if not "DEPRECATED" in value:
                                    state_list.append((key, value))
                           # state_list =  list(cmd_list.items()) #[(v, k) for v, k in cmd_list.items()]

                except:
                    state_list.append(("invalid", "invalid device type"))
                    self.logger.debug("Exception commandList",exc_info=True)

        except:
            self.logger.debug("Caught Exception device State Generator", exc_info=True)

        self.logger.debug(f"State List {state_list}")
        return state_list

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
        self.logger.debug("Starting event loop and setting up any connections")
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
        args = props.get("args","")

        if args != "":
            command = f"{command}={args}"


        self.logger.info(f"Sending Command {command} to appleTV Device ID {appleTVid}")
        foundDevice = False
        for appletvManager in self.appleTVManagers:

            if int(appletvManager.device_ID) == int(appleTVid):
                foundDevice = True
                self.logger.debug(f"Found correct AppleTV listener/manager. {appletvManager} and id {appletvManager.device_ID}")
                appletvManager.send_command(command, args)

        if foundDevice == False:
            self.logger.info("No command run.  The appleTV appears to have not been found.")

    def saveArtwork(self, valuesDict, typeId):

        self.logger.debug(f"saveArtwork Called {valuesDict} & {typeId}")
        props = valuesDict.props
        self.logger.debug(f"Props equal: {props}")

        if props["appleTV"] =="" or props["appleTV"]=="":
            self.logger.info("No AppleTV selected.")
            return

        width = None
        if props["width"] == "":
                width = None
        else:
            try:
                width = int(props["width"])
            except:
                self.logger.debug("Width Conversion, valueError at at guess.  Skipping.", exc_info=True)
                width = None

        appleTVid = props["appleTV"]
        self.logger.info(f"Saving current Artwork Width= {width} to appleTV Device ID {appleTVid}")
        foundDevice = False
        for appletvManager in self.appleTVManagers:

            if int(appletvManager.device_ID) == int(appleTVid):
                foundDevice = True
                self.logger.debug(f"Found correct AppleTV listener/manager. {appletvManager} and id {appletvManager.device_ID}")
                appletvManager.save_artwork(f"{self.saveDirectory}/{appletvManager.devicename}_Artwork.png", width, None)

        if foundDevice == False:
            self.logger.info("No artwork saved.  The appleTV appears to have not been found.")



    def speakText(self, valuesDict, typeId):
        self.logger.debug(f"speakText Called {valuesDict} & {typeId}")
        props = valuesDict.props
        self.logger.debug(f"Props equal: {props}")
        if props["appleTV"] =="" or props["appleTV"]=="":
            self.logger.info("No AppleTV selected.")
            return
        texttospeak = self.substitute(props.get("texttospeak",""))
        # allow variable device substitution
        appleTVid = props["appleTV"]
        self.logger.info(f"Speaking Text: {texttospeak} to appleTV Device ID {appleTVid}")
        foundDevice = False
        ffmpegpath = self.pathtoPlugin + '/ffmpeg/ffmpeg'
        #ffmpeg - i        Input.aiff - f        mp3 - acodec        libmp3lame - ab        192000 - ar        44100        Output.mp3

        try:
            p2 = subprocess.Popen(["say",str(texttospeak), "-o",self.speakPath+"/"+str(appleTVid)+".aiff" ])
            output, err = p2.communicate()
            self.logger.debug(str(texttospeak))
            self.logger.debug('say return code:' + str(p2.returncode) + ' output:' + str(
                output) + ' error:' + str(err))
        except Exception as e:
            self.logger.exception(u'Caught Exception within ffmpeg conversion')
        ffmpegpath = "./ffmpeg/ffmpeg"
        outputfile = self.speakPath+"/"+str(appleTVid)
        try:
            argstopass = '"' + ffmpegpath + '"' +' -y'+ ' -i "' +outputfile+".aiff" + '" -f mp3 "' + str(outputfile)+".mp3" + '"'
            self.logger.debug(argstopass)
            p1 = subprocess.Popen([argstopass], shell=True)
            outs, errs = p1.communicate(timeout=5)
           # self.logger.debug(str(argstopass))
            self.logger.debug('ffmpeg return code:' + str(p1.returncode) + ' output:' + str(
                outs) + ' error:' + str(errs))

        except subprocess.TimeoutExpired as e:
            p1.kill()
            outs, errs = p1.communicate()
            self.logger.info("{}".format(outs))
            self.logger.warning("{}".format(errs))
        except Exception as e:
            self.logger.exception(u'Caught Exception within ffmpeg conversion')

        self.logger.debug("{}".format(outs))
        self.logger.debug("{}".format(errs))

        command = "stream_file"
        args = str(outputfile)+".mp3"

        command = f"{command}={args}"

        self.logger.debug(f"Sending Command {command} to appleTV Device ID {appleTVid}")
        for appletvManager in self.appleTVManagers:
            if int(appletvManager.device_ID) == int(appleTVid):
                foundDevice = True
                self.logger.debug(f"Found correct AppleTV listener/manager. {appletvManager} and id {appletvManager.device_ID}")

                appletvManager.send_command(command,args )

        if foundDevice == False:
            self.logger.info("No Annoucement made.  The appleTV appears to have not been found.")

    async def process_playstatus(self, playstatus,  atv, time_start,deviceid, isAppleTV):
        try:
            #self.logger.debug(f"Process PlayStatus Called {playstatus}, {atv}, {atv.metadata} {time_start} and IndigoDeviceID {deviceid} ")
            self.logger.debug(f"PlayState DEVICE_state {playstatus.device_state}")
            #self.logger.debug(f"PlayState TITLE {playstatus.title}, & Position {playstatus.position} & Artist {playstatus.artist}  & media_type {playstatus.media_type} ")
            #self.logger.debug(f"PlayState TOTAL TIME {playstatus.total_time} & Series Name {playstatus.series_name} && Season_Numer {playstatus.season_number}")
            #self.logger.debug(f"PlayState EpisodeNo {playstatus.episode_number} & Content Identifier {playstatus.content_identifier} ")
            device = indigo.devices[deviceid]
            atv_appId = ""
            atv_app = None
            powerstate = False
            powerstate_string = "Unknown"
            if isAppleTV and atv.metadata.app !=None:
                atv_app = atv.metadata.app.name
            if atv_app !=None:
                atv_appId = atv.metadata.app.identifier
            self.logger.debug(f"App Playing {atv_appId} and App Name {atv_app}")
            playingState = "Standby"
            if atv is None:
                playingState = "Off"
            if isAppleTV:
                if atv.power.power_state == pyatv.const.PowerState.Off:
                    playingState = "Standby"
                    powerstate = False
                    powerstate_string = "Idle"
                elif atv.power.power_state == pyatv.const.PowerState.On:
                    powerstate = True
                    powerstate_string = "On"
            state = playstatus.device_state
            if state in (pyatv.const.DeviceState.Idle, pyatv.const.DeviceState.Loading):
                playingState = "Idle"
            if state == pyatv.const.DeviceState.Playing:
                playingState = "Playing"
            elif state == pyatv.const.DeviceState.Paused:
                playingState = "Paused"
            elif state == pyatv.const.DeviceState.Seeking:#, pyatv.const.DeviceState.Stopped):
                playingState = "Seeking"
            elif state ==pyatv.const.DeviceState.Stopped:
                playingState = "Stopped"

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
                {'key': 'PowerState', 'value': powerstate_string},
                {'key': 'onOffState', 'value': powerstate},
            ]
            device.updateStatesOnServer(stateList)
            if powerstate:
                device.updateStateImageOnServer(indigo.kStateImageSel.PowerOn)
            else:
                device.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
        except:
            self.logger.exception("process_playlist error")

    async def _async_stop(self):
        while True:
            await asyncio.sleep(5.0)
            if self.stopThread:
                break

    def menu_callback(self, valuesDict, *args, **kwargs):  # typeId, devId):
        self.logger.debug(f"Menu callback: returning valuesDict: \n {valuesDict}")
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

    async def matchatv_nopairing(self, identifier):
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
                    self.logger.debug(f"Found Matching Device {atv.identifier}, no Pairing.")
                    self._event_loop.create_task(self.no_pairing_needed(atv))
                    return

    async def return_MatchedappleTVs(self, identifier, devicename, ipaddress):
        self.logger.debug("Returning all ATVS")
        if ipaddress !="UNKNOWN":
            atvs = await pyatv.scan(self._event_loop, hosts=[ipaddress],timeout=15)
        else:
            atvs = await pyatv.scan(self._event_loop, timeout=15)
        if not atvs:
            self.logger.info("This deivce was not found.  Try power cycling and try again.")
            return None
        else:
            self.logger.debug(f"atvs {atvs}")
            for atv in atvs:
                self.logger.debug(f"Device Identifer: {identifier}  && appleTV {atv.identifier}")
                if identifier == str(atv.identifier):
                    self.logger.debug(f"Found Matching Device {atv.identifier}, start Pairing.")
                    self._event_loop.create_task(self.one_pairing(atv, devicename))
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

    async def get_appleTVs(self, forceDiscovery):
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
                    self.createNewDevice(atv, forceDiscovery)
        except:
            self.logger.exception("Exception in get appleTVs")

    async def get_appleTVs_IP(self, forceDiscovery, hosts):
        """Find a device and print what is playing."""
        try:
            self.logger.info(f"Scanning IP address: {hosts} for an appleTV device, and creating Indigo device if doesn't already exist")
            atvs = await pyatv.scan(self._event_loop, hosts=[hosts])
            if not atvs:
                self.logger.info("No device found")
                return None
            else:
                self.logger.debug(f"atvs {atvs}")
                #output = "\n\n".join(str(result) for result in atvs)
                #self.logger.info(f"{output}")
                for atv in atvs:
                    self.createNewDevice(atv, forceDiscovery)
        except:
            self.logger.exception("Exception in get appleTVs_IP")

    def createNewDevice(self, atv, forceDiscovery):

        ip = str(atv.address)
        name = atv.name
        operating_system = atv.device_info.operating_system
        mac = atv.device_info.mac
        model = atv.device_info.model
        identifier = atv.identifier

        self.logger.debug(f"\n{ip}\n{name}\n{mac}\n{model}\n{operating_system}")

        for dev in indigo.devices.iter("self"):
            if "identifier" not in dev.states: continue
            if str(dev.states["identifier"]) == str(identifier):
                self.logger.debug(f"Found exisiting device same Identifier. Skipping: {dev.name},but now checking IP address")
                oldip = dev.states["ip"]
                if str(oldip) != str(ip):
                    self.logger.info(f"Found existing device with a different IP Address, updating this IP Address")
                    dev.updateStateOnServer(key="ip", value=str(ip))
                    localPropsCopy = dev.ownerProps
                    localPropsCopy["IP"] = str(ip)
                    dev.replacePluginPropsOnServer(localPropsCopy)
                return

        if model !=  pyatv.const.DeviceModel.Unknown or forceDiscovery:
            devProps = {}
            devProps["isAppleTV"] = True
            devProps["SupportsOnState"] = False
            devProps["SupportsSensorValue"] = False
            devProps["SupportsStatusRequest"] = False
            devProps["AllowOnStateChange"] = False
            devProps["AllowSensorValueChange"] = False
            devProps["IP"] = str(ip)
            devProps["MAC"] = str(mac)
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


