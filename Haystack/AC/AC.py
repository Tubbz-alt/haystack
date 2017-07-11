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

cnx = mysql.connector.connect(user='root', host='127.0.0.1', database='agentsandservices')
identification = spade.AID.aid(name="ac@127.0.0.1", addresses=["xmpp://ac@127.0.0.1"])

class ReceiveMessageAC(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "Message received: " + self._receive().getContent()
class ReceiveAgent(spade.Behaviour.EventBehaviour):
    def _process(self):            
        print "Detected new agent!"
        strList = self._receive().getContent().split(",")
        agentName = strList[0]
        agentVersion = strList[1]
        agentOS = strList[2]
        agentArchitecture = strList[3]
        agentStatus = strList[4]
        success = AC.newAgent(agentName, agentVersion, agentOS, agentArchitecture, agentStatus)
            
        if success == 1:
            print "Agent added"
        else:
            msg = spade.ACLMessage.ACLMessage()
            msg.setPerformative("inform")
            msg.addReceiver(spade.AID.aid(agentName+"@127.0.0.1",["xmpp://"+agentName+"@127.0.0.1"]))
            msg.setOntology("message")
            msg.setContent("AC - ReceiveAgent(): Failed to add agent to database.")
            self.myAgent.send(msg)
class AgentController(spade.Agent.Agent):
    def agentIDfromName(self, agentName):
        global cnx
        cursor = cnx.cursor()
        query = ("SELECT agentID FROM agents WHERE agentName = \'{}\'".format(agentName))
        cursor.execute(query)
        agentID = cursor.fetchone()
        cursor.close()
        return agentID[0]

    def serviceIDfromName(self, serviceName):
        global cnx
        cursor = cnx.cursor()
        query = ("SELECT serviceID FROM services WHERE serviceName = \'{}\'".format(serviceName))
        cursor.execute(query)
        serviceID = cursor.fetchone()
        cursor.close()
        return serviceID[0]
        
    def printAgents(self, command):
        global cnx
        cursor = cnx.cursor()
        if command == 2:
            query = ("SELECT agentID, agentName, agentVersion, agentOS, agentArchitecture, agentStatus FROM agents WHERE agentStatus = 1")
        elif command == 3:
            query = ("SELECT agentID, agentName, agentVersion, agentOS, agentArchitecture, agentStatus FROM agents WHERE agentStatus = 0")
        else:
            query = ("SELECT agentID, agentName, agentVersion, agentOS, agentArchitecture, agentStatus FROM agents")
        cursor.execute(query)
        for (agentID, agentName, agentVersion, agentOS, agentArchitecture, agentStatus) in cursor:
            print("{}, {}, {}, {}, {}, {}".format(agentID, agentName, agentVersion, agentOS, agentArchitecture, agentStatus))
        cursor.close()

    def newAgent(self, agentName, agentVersion, agentOS, agentArchitecture, agentStatus):
        global cnx
        r = 1
        cursor = cnx.cursor()
        query = ("INSERT INTO agents(agentName, agentVersion, agentOS, agentArchitecture, agentStatus) VALUES(\"{}\", {}, \"{}\", \"{}\", {})".format(agentName, agentVersion, agentOS, agentArchitecture, agentStatus))
        
        try:
            cursor.execute(query)
        except:
            print("Error: ", sys.exc_info()[0])
            r = 0
        cursor.close()
        return r

    def removeAgent(self, agentName):
        global cnx
        cursor = cnx.cursor()
        query = ("DELETE FROM agents WHERE agentName = \'{}\'".format(agentName))
        cursor.execute(query)
        cursor.close()

    def controlAgent(self, agentName):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid(agentName+"@127.0.0.1",["xmpp://"+agentName+"@127.0.0.1"]))
        msg.setOntology("command")
        msg.setContent("0")
        self.send(msg)
        quit = False
        while quit == False:
            print agentName + " Menu"
            print "q: Quit"
            message = raw_input("Command: ")
            if message == "q":
                quit = True
            else:
                msg = spade.ACLMessage.ACLMessage()
                msg.setPerformative("inform")
                msg.addReceiver(spade.AID.aid(agentName+"@127.0.0.1",["xmpp://"+agentName+"@127.0.0.1"]))
                msg.setOntology("command")
                msg.setContent(message)
                self.send(msg)
        
    def printServices(self):
        global cnx  
        cursor = cnx.cursor()
        query = ("SELECT serviceID, serviceName FROM services")
        cursor.execute(query)
        for (serviceID, serviceName) in cursor:
            print("{}, {}".format(serviceID, serviceName))
        cursor.close()

    def newService(self, serviceName):
        global cnx
        cursor = cnx.cursor()
        query = ("INSERT INTO services(serviceName) VALUES(\"{}\")".format(serviceName))
        cursor.execute(query)
        cursor.close()

    def removeService(self, serviceName):
        global cnx
        cursor = cnx.cursor()
        query = ("DELETE FROM services WHERE serviceName = \'{}\'".format(serviceName)) 
        cursor.execute(query)
        cursor.close()

    def printAgentsServices(self):
        global cnx
        cursor = cnx.cursor()
        query = ("SELECT agentID, serviceID FROM agents_services")
        cursor.execute(query)
        for (agentID, serviceID) in cursor:
            print("{}, {}".format(agentID, serviceID))
        cursor.close()

    def addServiceToAgent(self, agentName, serviceName):
        global cnx

        agentID = self.agentIDfromName(agentName)     
        serviceID = self.serviceIDfromName(serviceName)
    
        cursor = cnx.cursor()
        query = ("INSERT INTO agents_services(agentID, serviceID) VALUES({}, {})".format(agentID, serviceID))
        cursor.execute(query)
        cursor.close()

    def removeServiceFromAgent(self, agentName, serviceName):
        global cnx
        
        agentID = self.agentIDfromName(agentName)
        serviceID = self.serviceIDfromName(serviceName)

        cursor = cnx.cursor()
        query = ("DELETE FROM agents_services WHERE agentID = {} AND serviceID = {}".format(agentID, serviceID))
        cursor.execute(query)
        cursor.close()

    def _setup(self):
        print "_setup"
        newAgentTemplate = spade.Behaviour.ACLTemplate()
        newAgentTemplate.setOntology("newAgent")
        nat = spade.Behaviour.MessageTemplate(newAgentTemplate)
        
        receiveMessageTemplate = spade.Behaviour.ACLTemplate()
        receiveMessageTemplate.setOntology("message")
        rmt = spade.Behaviour.MessageTemplate(receiveMessageTemplate)

        self.addBehaviour(ReceiveMessageAC(),rmt)
        self.addBehaviour(ReceiveAgent(),nat)        
    
if __name__ == "__main__":
    AC = AgentController("ac@127.0.0.1", "secret")
    AC.start()

quit = False
while quit == False:
    print "\n"
    print "AC Menu"
    print "1. List Agents"
    print "2. New Agent"
    print "3. Remove Agent"
    print "4. List Services"
    print "5. New Service"
    print "6. Remove Service"
    print "7. List Agents_Services"
    print "8. Add service to agent"
    print "9. Remove service from agent"
    print "10. Control agent"
    print "c. Commit"
    print "q. Quit"
    command = raw_input("Command: ")
    print "\n"

    if command == "1":
        print "1. All agents"
        print "2. Active agents"
        print "3. Inactive agents"
        command = raw_input("Command: ")
        if command == "1":
            AC.printAgents(1)
        elif command == "2":
            AC.printAgents(2)
        elif command == "3":
            AC.printAgents(3)
        else:
            print "Invalid command"
    elif command == "2":
        agentName = raw_input("agentName: ")
        agentVersion = raw_input("agentVersion: ")
        agentOS = raw_input("agentOS: ")
        agentArchitecture = raw_input("agentArchitecture: ")
        agentStatus = raw_input("agentStatus: ")
        AC.newAgent(agentName, agentVersion, agentOS, agentArchitecture, agentStatus)
    elif command == "3":
        agentName = raw_input("agentName: ")
        AC.removeAgent(agentName)
    elif command == "4":
        AC.printServices()
    elif command == "5":
        serviceName = raw_input("serviceName: ")
        AC.newService(serviceName)
    elif command == "6":
        serviceName = raw_input("serviceName: ")
        AC.removeService(serviceName)
    elif command == "7":
        AC.printAgentsServices()
    elif command == "8":
        agentName = raw_input("agentName: ")
        serviceName = raw_input("serviceName: ")
        AC.addServiceToAgent(agentName, serviceName)
    elif command == "9":
        agentName = raw_input("agentName: ")
        serviceName = raw_input("serviceName: ")
        AC.removeServiceFromAgent(agentName, serviceName)
    elif command == "10":
        agentName = raw_input("agentName: ")
        AC.controlAgent(agentName)
    elif command == "c":
        cnx.commit()
    elif command == "q":
        quit = True
    else:
        print "Invalid command"

cnx.close()
print "done"

