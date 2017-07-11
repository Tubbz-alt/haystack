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

import pywin
import pywinauto

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import mysql.connector

agentName = raw_input("Agent name (notepad): ")
identification = spade.AID.aid(name=agentName+"@127.0.0.1", addresses=["xmpp://"+agentName+"@127.0.0.1"])

app = 0

class ReceiveMessage(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "Message received: " + self._receive().getContent()
class ReceiveCommand(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "ANB _process"
        lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        strList = self._receive().getContent().split(",")
        if strList[0] == "0":
            msg = spade.ACLMessage.ACLMessage()
            msg.setPerformative("inform")
            msg.addReceiver(spade.AID.aid("ac@127.0.0.1",["xmpp://ac@127.0.0.1"]))
            msg.setOntology("message")
            msg.setContent("\n0. List Commands (0)\n1. Open Notepad (1)\n2. Open File (2,directory/filename)\n3. Type (3,textToType)\n4. Save As... (4,directory/filename)\n5. Close (5)")
            a.send(msg)
        elif strList[0] == "1":
            global app 
            app = pywinauto.application.Application().Start(cmd_line=u'notepad.exe')
        elif strList[0] == "2":
            menu_item = app.UntitledNotepad.MenuItem(u'&File->&Open')
            menu_item.ClickInput()
            # figure out logic of opening a file when unsaved changes are present in current notepad
            #window = app.Dialog
            #window.Wait('ready')
            #button = window.Button2
            #button.ClickInput()
            window = app.Open
            window.Wait('ready')
            edit = window.Edit
            edit.SetFocus()
            edit.TypeKeys(strList[1])
            button = window[u'&Open']
            button.ClickInput()
        elif strList[0] == "3":
            app.UntitledNotepad.Edit.TypeKeys(strList[1], with_spaces=True)
        elif strList[0] == "4":
            menu_item = app.UntitledNotepad.MenuItem(u'&File->Save &As...')
            menu_item.ClickInput()
            window = app.Dialog
            window.Wait('ready')
            combobox = window[u'4']
            combobox.SetFocus()
            combobox.TypeKeys(strList[1])
            button = window[u'&Save']
            button.ClickInput()
            button = window[u'&Yes']
            button.ClickInput()
        elif strList[0] == "5":
            menu_item = app.UntitledNotepad.MenuItem(u'&File->E&xit')
            menu_item.ClickInput()
            window = app.Dialog
            window.Wait('ready')
            button = window.Button2
            button.ClickInput()
class AgentNotepad(spade.Agent.Agent):
    def _setup(self):
        print "_setup"
        receiveCommandTemplate = spade.Behaviour.ACLTemplate()
        receiveCommandTemplate.setOntology("command")
        rct = spade.Behaviour.MessageTemplate(receiveCommandTemplate)        
        self.addBehaviour(ReceiveCommand(),rct)
        
        receiveMessageTemplate = spade.Behaviour.ACLTemplate()
        receiveMessageTemplate.setOntology("message")
        rmt = spade.Behaviour.MessageTemplate(receiveMessageTemplate)
        self.addBehaviour(ReceiveMessage(),rmt)

if __name__ == "__main__":
    a = AgentNotepad(agentName+"@127.0.0.1", "secret")  
    a.start()

quit = False
while quit == False:
    print "\n"
    print "AgentNotepad Menu"
    print "1. Inform AC that I exist"
    print "2. Change agent name"
    print "q. Quit"
    command = raw_input('Command: ')
    print "\n"
    if command == "1":
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("ac@127.0.0.1",["xmpp://ac@127.0.0.1"]))
        msg.setContent(agentName+",1.01,Windows 7,x86,1")
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
