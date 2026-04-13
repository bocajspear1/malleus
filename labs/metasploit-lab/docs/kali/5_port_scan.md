# Port Scanning with NMap

Services listen on the network via "ports." This allows clients to know where to send what services and endpoints know what network traffic is going to what service.

TCP ports listen for connections and attempt to form a full connection (with the "three-way handshake") when they are connected to. We don't HAVE to fully connect and talk to the service, but we can take advantage of the connection building process to determine what services are running by what ports try to make a full connection. If no service is listening on a port, it won't respond or try to make the full connection.

To make NMap do a port scan, which will check selected ports to see if they're open, we drop the `-sn` and set a port range with `-p`.

We can use ranges (`1-2000`), comma separated lists (`1,2`), or just `-` if we want to scan all ports.

Run NMap with all ports to see all possible ports open. If you don't set this, only the top 1000 ports will be scanned.

```
nmap -p- TARGET
```