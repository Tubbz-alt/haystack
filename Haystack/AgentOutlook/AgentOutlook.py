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
import sys

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

import win32com.client
from win32com.client import Dispatch, constants
import pythoncom

import pywin
import pywinauto

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import mysql.connector

agentName = raw_input("Agent name (outlook): ")
identification = spade.AID.aid(name=agentName+"@127.0.0.1", addresses=["xmpp://"+agentName+"@127.0.0.1"])

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
class MailController(object):
    __metaclass__ = Singleton
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def run_in_thread(self):
        pythoncom.CoInitialize()
        self.obj = win32com.client.Dispatch(pythoncom.CoGetInterfaceAndReleaseStream(self.xl_id, pythoncom.IID_IDispatch))
    def start(self):
        try:
            #pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
            self.ol = 0x0
            self.obj = win32com.client.Dispatch("Outlook.Application")
            self.mailWindow = self.obj.CreateItem(self.ol)
            self.xl_id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, self.obj)
            
            self.thread = threading.Thread(target=self.run_in_thread)
            self.thread.start()
            self.thread.join()
        except pythoncom.com_error:
            # already initialized 
            pass
    def displayMail(self, subject, address, body):
        self.ol = 0x0
        self.obj = win32com.client.Dispatch("Outlook.Application")
        self.mailWindow = self.obj.CreateItem(self.ol)
        self.xl_id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, self.obj)
            
        self.thread = threading.Thread(target=self.run_in_thread)
        self.thread.start()
        self.thread.join()
        self.mailWindow.Subject = "test"
        #self.mailWindow.BodyEncoding = System.Text.Encoding.ASCII
        self.mailWindow.Body = "testing"
        self.mailWindow.To = "garret.seppala@pnnl.gov"
        self.mailWindow.display()

        #for c in body:
        #    self.mailWindow.Body += c
        #    time.sleep(0.01)
    def sendMail(self):
        self.mailWindow.Send()
    def closeMail(self):
        self.mailWindow.Close(0)
class ReceiveMessage(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "Message received: " + self._receive().getContent()
class ReceiveCommand(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "ANB _process"
        pythoncom.CoInitialize()
        
        strList = self._receive().getContent().split(",")
        if strList[0] == "0":
            msg = spade.ACLMessage.ACLMessage()
            msg.setPerformative("inform")
            msg.addReceiver(spade.AID.aid("ac@127.0.0.1",["xmpp://ac@127.0.0.1"]))
            msg.setOntology("message")
            msg.setContent("\n0. List Commands (0)\n1. Send email (1,address,title,body)\n2. Close (2)")
            a.send(msg)
        elif strList[0] == "1":
            subject = "Lorem Ipsum"
            address = "garret.seppala@pnnl.gov"
            body = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
            mc.displayMail(subject, address, body)
            #mc.sendMail()
        elif strList[0] == "2":
            mc.closeMail()
class AgentOutlook(spade.Agent.Agent):
    def _setup(self):
        print "_setup"
        receiveCommandTemplate = spade.Behaviour.ACLTemplate()
        # python spade is really hard to deal with . idk what to do at all. 
        receiveCommandTemplate.setOntology("command")
        rct = spade.Behaviour.MessageTemplate(receiveCommandTemplate)
        self.addBehaviour(ReceiveCommand(),rct)
        
        receiveMessageTemplate = spade.Behaviour.ACLTemplate()
        receiveMessageTemplate.setOntology("message")
        rmt = spade.Behaviour.MessageTemplate(receiveMessageTemplate)
        self.addBehaviour(ReceiveMessage(),rmt)

if __name__ == "__main__":
    a = AgentOutlook(agentName+"@127.0.0.1", "secret")  
    a.start()
    mc = MailController()
    mc.start()
    #mc.displayMail()
    #mc.closeMail()

quit = False
while quit == False:
    print "\n"
    print "AgentOutlook Menu"
    print "1. Inform AC that I exist"
    print "2. Change agent name"
    print "q. Quit"
    command = raw_input('Command: ')
    print "\n"
    if command == "1":
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("ac@127.0.0.1",["xmpp://ac@127.0.0.1"]))
        msg.setContent(agentName+",1.01,Windows 10,x86_64,1")
        msg.setOntology("newAgent")
        a.send(msg)
    elif command == "2":
        agentName = raw_input("Agent name: ")
        a.stop()
        a = AgentNotepad(agentName+"@127.0.0.1", "secret")  
        a._setup()
        a.start()
    elif command == "q":
        quit = True
    else:
        print "Invalid command"
