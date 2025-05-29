import socket


def send_magic_packet(mac: str, sock_factory=socket.socket):
    # MAC アドレスをバイト列に変換
    mac_bytes = bytes.fromhex(mac.replace(":", "").replace("-", ""))
    packet = b"\xff" * 6 + mac_bytes * 16

    with sock_factory(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, ("<broadcast>", 9))
