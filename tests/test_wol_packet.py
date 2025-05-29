# tests/test_wol_packet.py
from wake.wol import send_magic_packet


class DummySocket:
    def __init__(self, *args, **kwargs):
        self.sent = []
        self.opts = []

    def setsockopt(self, level, optname, value):
        # ブロードキャスト設定が呼ばれたかを記録
        self.opts.append((level, optname, value))

    def sendto(self, packet, addr):
        # 送信ペイロードと宛先を記録
        self.sent.append((packet, addr))

    # with 文用メソッド
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


def test_send_magic_packet_with_dummy():
    dummy = DummySocket()
    # sock_factory に常に同じ dummy を返す lambda を渡す
    send_magic_packet("AA:BB:CC:DD:EE:FF", sock_factory=lambda *a, **k: dummy)

    # 期待されるマジックパケット
    expected = b"\xff" * 6 + bytes.fromhex("aabbccddeeff") * 16
    # sendto が一度だけ呼ばれ、正しいペイロードとアドレスが使われているか
    assert dummy.sent == [(expected, ("<broadcast>", 9))]
    # ブロードキャストオプションの設定チェック
    import socket

    assert (socket.SOL_SOCKET, socket.SO_BROADCAST, 1) in dummy.opts
