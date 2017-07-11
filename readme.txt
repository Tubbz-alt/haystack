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

-----------------------------------------------------------------------------------------------------------------

READ ME 

Haystack will have the capabiliy to control many agents across a network, telling them to perform certain actions, such as creating new files, editing files, sending emails, browsing the web, etc. 
There will be a central process that keeps track of and controls the subprocesses, or "agents" that are sent out. 

Haystack has a few dependencies to properly compile and execute, here they are listed. 
- Python 2.7 (Anaconda)
- pywinauto, selenium, mysql connector, spade
- A MySQL database must be running. 
- XAMPP was/is used during early development stages to host several processes. 

