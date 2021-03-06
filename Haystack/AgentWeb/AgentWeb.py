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
import random

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

import pywin
import pywinauto

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import mysql.connector

agentName = raw_input("Agent name (web): ")
identification = spade.AID.aid(name=agentName+"@127.0.0.1", addresses=["xmpp://"+agentName+"@127.0.0.1"])   
    
urlList = []
timeUrlProbList = []
frequency = 10
visits = 10
driver = 0

class ReceiveMessage(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "Message received: " + self._receive().getContent()
class ReceiveCommand(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "ANB _process"
        global urlList
        global driver
        global frequency
        global visits
        global timeUrlProbList
        strList = self._receive().getContent().split(",")
        if strList[0] == "0":
            msg = spade.ACLMessage.ACLMessage()
            msg.setPerformative("inform")
            msg.addReceiver(spade.AID.aid("ac@127.0.0.1",["xmpp://ac@127.0.0.1"]))
            msg.setOntology("message")
            content = "\n0. List Commands (0)\n"
            content = content + "1. Open Firefox (1)\n"
            content = content + "2. Add site(s) to possibilities (2,url1,url2,url3,...urln)\n" 
            content = content + "3. Remove site(s) from possibilities (3,url1,url2,url3...)\n" 
            content = content + "4. List sites (4)\n" 
                                                      #(5,time1-time2|urlNum-%|urlNum-%|...urlNum-%,time2-time3|urlNum-%...) 
            content = content + "5. Define probability (5,0-2|1-0.1|2-0.2|...n-0.5,2-10|...)\n" 
            content = content + "6. Go #times - default 1(6,1)\n" 
            content = content + "7. Frequency in seconds (7,10)\n" 
            content = content + "8. Visits (8,10)\n" 
            content = content + "9. Close (9)" 
            msg.setContent(content) 
            a.send(msg) 
        elif strList[0] == "1":
            driver = webdriver.Firefox() 
        elif strList[0] == "2":
            iterstr = strList                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
            iterstr.remove("2")
            for str in iterstr:
                urlList.append(str) #https://www.google.com
        elif strList[0] == "3": 
            iterstr = strList
            iterstr.remove("3")
            for str in iterstr:
                urlList.remove(str)
        elif strList[0] == "4": 
            i = 1
            msgTxt = "\nURLs:\n"
            for str in urlList:
                msgTxt = msgTxt + "{}: ".format(i) + str + "\n"
                i = i + 1
            msgTxt = msgTxt + "\n"
            msg = spade.ACLMessage.ACLMessage()
            msg.setPerformative("inform")
            msg.addReceiver(spade.AID.aid("ac@127.0.0.1",["xmpp://ac@127.0.0.1"]))
            msg.setOntology("message")
            msg.setContent(msgTxt)
            a.send(msg)
        elif strList[0] == "4.1":
            msgTxt = "\nURLs w/ prob:\n"
            for item in timeUrlProbList:
                msgTxt = msgTxt + "time: " + item[0][0] + "-" + item[0][1] + "\n"
                msgTxt = msgTxt + "url: " + item[1] + "\n"
                msgTxt = msgTxt + "prob: " + item[2][1] + "\n"
                msgTxt = msgTxt + "\n"
            msg = spade.ACLMessage.ACLMessage()
            msg.setPerformative("inform")
            msg.addReceiver(spade.AID.aid("ac@127.0.0.1",["xmpp://ac@127.0.0.1"]))
            msg.setOntology("message")
            msg.setContent(msgTxt)
            a.send(msg)
        elif strList[0] == "5": #(5,time1-time2|url1-%|url2-%|...urlN-%,time2-time3|url1-%...) # 5,tim,e
            iterstr = strList
            iterstr.remove("5")
            for str in iterstr:
                itemList = str.split("|")
                timeRange = itemList.pop(0).split("-")
                timeBegin = timeRange[0]
                timeEnd = timeRange[1]
                for item in itemList:
                    urlProb = item.split("-")
                    urlNum = urlProb[0]
                    prob = urlProb[1]
                    timeUrlProbList.append([[timeBegin,timeEnd],urlNum,urlProb]) # [[[0-2],1,0.5],[[2-5],2,0.3]] 
        elif strList[0] == "6": # go 
            # build ordered list to VISIT during the operation 
            if len(strList) > 1: 
                times = int(strList[1]) 
            else: 
                times = 1 
            while abs(times) > 0: 
                urlVisitList = [] 
                i = 0 
                while i < int(visits): 
                    for item in timeUrlProbList: 
                        if(int(item[0][0]) <= datetime.now().hour and datetime.now().hour < int(item[0][1])): #within time range? 
                            #print "{} < {} < {}".format(item[0][0], datetime.now().hour, item[0][1]) 
                            if(random.uniform(0,1) > float(item[2][1])): #dice roll 
                                urlVisitList.append(urlList[int(item[1]) - 1]) #add url to list 
                    i = i + 1 
                for url in urlVisitList: 
                    driver.get(url) 
                    time.sleep(int(frequency)) 
                times = times - 1 
        elif strList[0] == "7": 
            frequency = strList[1] 
        elif strList[0] == "8": 
            visits = strList[1] 
        elif strList[0] == "9": 
            driver.close() 
class AgentWeb(spade.Agent.Agent): 
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
    a = AgentWeb(agentName+"@127.0.0.1", "secret")  
    a.start()

quit = False
while quit == False:
    print "\n"
    print "AgentWeb Menu"
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
        a = AgentWeb(agentName+"@127.0.0.1", "secret")  
        a._setup()
        a.start()
    elif command == "q":
        quit = True
    else:
        print "Invalid command"
