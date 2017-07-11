# Haystack - An automation tool that deploys agents to computers across a network to mimick human-like behaviors.
# Copyright (C) 2016 - 2017 Pacific Northwest National Laboratory

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
  
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
  
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import spade
import os
import subprocess
import threading
import win32com
import time

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

import pywin
import pywinauto

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import mysql.connector

cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='agentsandservices')
identification = spade.AID.aid(name="s@127.0.0.1", addresses=["xmpp://s@127.0.0.1"])

message = ""

class SendMessageBehav(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "_process"
class AgentSender(spade.Agent.Agent):            
    def _setup(self):
        print "_setup"
        self.addBehaviour(SendMessageBehav(), None)

class SvcSender(win32serviceutil.ServiceFramework):
    _svc_name_ = "TestSvcSend01"
    _svc_display_name_ = "Test Service Send 01"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_,''))
        self.main()

    def main(self):
        s = AgentSender("s@127.0.0.1", "secret")
        s.start()

        quit = False
        while quit == False:
            msg = spade.ACLMessage.ACLMessage()
            msg.setPerformative("inform")
            msg.addReceiver(spade.AID.aid("r@127.0.0.1",["xmpp://r@127.0.0.1"]))
            message = raw_input("Message: ")
            msg.setContent(message)
            s.send(msg)
            choice = raw_input('Q for quit: ')
            if choice == 'q':
                quit = True
        
if __name__ == "__main__":
    #win32serviceutil.HandleCommandLine(SvcSender)
    s = AgentSender("s@127.0.0.1", "secret")
    s.start()

    quit = False
    while quit == False:
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("r@127.0.0.1",["xmpp://r@127.0.0.1"]))
        message = raw_input("Message: ")
        msg.setContent(message)
        s.send(msg)
        if message == 'q':
            quit = True

cnx.close()
