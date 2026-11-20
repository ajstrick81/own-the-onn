#!/usr/bin/env python3
"""Send standard LAN discovery queries so a running LAN capture records what the onn answers.

Usage: python -I tools/lan_probe.py <this-PC's-LAN-IPv4>

Start the LAN capture first (see method/README.md "LAN-side capture"), then run this once. It sends, from the given
interface address: SSDP M-SEARCH for ssdp:all, DIAL and UPnP MediaRenderer (3x each, MX 2) to 239.255.255.250:1900,
and one mDNS PTR query each for common service types to 224.0.0.251:5353. It only asks; it doesn't listen or parse
replies (the capture does). Ordinary discovery traffic, the same any phone or smart speaker sends.
"""
import socket
import struct
import sys
import time

SSDP_TARGETS = ["ssdp:all", "urn:dial-multiscreen-org:service:dial:1",
                "urn:schemas-upnp-org:device:MediaRenderer:1"]
MDNS_SERVICES = ["_googlecast._tcp.local", "_airplay._tcp.local", "_http._tcp.local",
                 "_androidtvremote2._tcp.local", "_services._dns-sd._udp.local"]


def sock(src):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(src))
    s.bind((src, 0))
    return s


def ssdp(src, st):
    msg = ("M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\n"
           'MAN: "ssdp:discover"\r\nMX: 2\r\nST: %s\r\nUSER-AGENT: lan-audit/1\r\n\r\n' % st)
    s = sock(src)
    for _ in range(3):
        s.sendto(msg.encode(), ("239.255.255.250", 1900))
        time.sleep(0.4)
    s.close()
    print("sent SSDP M-SEARCH ST=%s" % st)


def mdns(src, name):
    hdr = struct.pack(">HHHHHH", 0, 0, 1, 0, 0, 0)
    q = b"".join(bytes([len(p)]) + p.encode() for p in name.split(".")) + b"\x00"
    q += struct.pack(">HH", 12, 1)  # PTR, IN
    s = sock(src)
    s.sendto(hdr + q, ("224.0.0.251", 5353))
    s.close()
    print("sent mDNS PTR %s" % name)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    for st in SSDP_TARGETS:
        ssdp(src, st)
        time.sleep(0.5)
    for svc in MDNS_SERVICES:
        mdns(src, svc)
        time.sleep(0.3)
    print("probe done")


if __name__ == "__main__":
    main()
