# Service and Script Scanning with NMap

NMap can attempt to identify services using a service scan (-sV) and extra data using a scripts scan (-sC).

This will get you a lot more information about the service, as this time, a full connection is made and NMap attempts to try certain protocols and reads the responses.


```
nmap -p- -sV -sC TARGET
```