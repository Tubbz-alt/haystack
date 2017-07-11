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

import win32com.client
from win32com.client import Dispatch, constants

import pywin
import pywinauto

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import mysql.connector

agentName = raw_input("Agent name (outlook): ")
identification = spade.AID.aid(name=agentName+"@127.0.0.1", addresses=["xmpp://"+agentName+"@127.0.0.1"])

def sendEmail():
    print "enter {}".format(random.uniform(0,1))
    driver = webdriver.Firefox()
    url = "http://www.python.org"
    driver.get(url)
    assert "Python" in driver.title
    elem = driver.find_element_by_name("q")
    elem.clear()
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source
    driver.close()
    print "leave"

sendEmail()

#new.Send()
