#CREATE table agents_services
#(
#agentID int,
#serviceID int,
#CONSTRAINT agent_service_pk PRIMARY KEY (agentID, serviceID),
#CONSTRAINT agent_fk FOREIGN KEY (agentID) REFERENCES agents(agentID),
#CONSTRAINT service_fk FOREIGN KEY (serviceID) REFERENCES services(serviceID)
#);

SELECT agentID, agentName, agentVersion, agentOS, agentArchitecture, agentStatus FROM agents WHERE agentStatus = 0;
SeLeCt agentID, agentName ,agentVersion, agentOS, agentArchitecture, agentStatus fROM agents where agentStatus = 1;
