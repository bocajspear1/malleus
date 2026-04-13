# Ping Scanning with NMap

NMap can be used to ping scan to determine what systems are available on the network.

Check out some of the many options you can use with nmap with:

```
nmap -h
```

### Running a ping scan

Use the `-sn` flag to do a ping scan of the network the Kali is attached to. Use `ip addr` to get the IP.

Ranges (1-5), network masks (/24), and comma separated values can be used to indicate the target in NMap.

```
nmap -sn TARGET
```

Scan the entire range to determine our target.

> It might be a good idea to use `--exclude` to ignore our own IP.
