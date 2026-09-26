"""Onn privacy study: passthrough-only metadata logger for mitmproxy --mode wireguard.

Never decrypts: every TLS/QUIC ClientHello is marked ignore_connection, so the
connection is relayed byte-for-byte. Logs only DNS questions, TLS SNI, and the
destination of every connection, as JSON lines, to $ONN_CAP_LOG (default
onn_capture.jsonl). The scenario label comes from $ONN_SCENARIO.
"""
import json
import os
import time

from mitmproxy import dns, tls
from mitmproxy.connection import Server

LOG = os.environ.get("ONN_CAP_LOG", "onn_capture.jsonl")
SCEN = os.environ.get("ONN_SCENARIO", "?")


def _w(rec):
    rec["t"] = round(time.time(), 3)
    rec["scen"] = SCEN
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _addr(a):
    return f"{a[0]}:{a[1]}" if a else None


class PassthroughLogger:
    def tls_clienthello(self, data: tls.ClientHelloData):
        data.ignore_connection = True  # passthrough: no interception, ever
        s = data.context.server
        _w({"k": "tls", "sni": data.client_hello.sni,
            "alpn": [p.decode(errors="replace") for p in (data.client_hello.alpn_protocols or [])],
            "dst": _addr(s.address), "proto": s.transport_protocol})

    def dns_request(self, flow: dns.DNSFlow):
        for q in flow.request.questions:
            _w({"k": "dns", "q": q.name, "type": dns.types.to_str(q.type)})

    def dns_response(self, flow: dns.DNSFlow):
        if flow.response:
            ans = [str(a) for a in flow.response.answers][:6]
            for q in flow.request.questions:
                _w({"k": "dnsans", "q": q.name, "a": ans})

    def server_connect(self, data):
        s: Server = data.server
        _w({"k": "conn", "dst": _addr(s.address), "proto": s.transport_protocol,
            "sni": s.sni})

    def request(self, flow):
        # only reached for plaintext HTTP (TLS is ignored above)
        _w({"k": "http", "host": flow.request.pretty_host, "method": flow.request.method,
            "path": flow.request.path[:200], "bytes": len(flow.request.raw_content or b"")})


addons = [PassthroughLogger()]
