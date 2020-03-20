import unittest

from mintersdk.sdk.transactions import MinterSendCoinTx
from mintersdk.sdk.deeplink import MinterDeeplink


class TestDeeplink(unittest.TestCase):
    def test_fulltx(self):
        tx = MinterSendCoinTx(
            coin='BIP', to='Mx18467bbb64a8edf890201d526c35957d82be3d95',
            value=1.23456789, nonce=1, gas_coin='MNT', gas_price=1,
            payload='Check payload'
        )
        deeplink = MinterDeeplink(tx=tx)

        self.assertEqual(
            MinterDeeplink.BASE_URL + '?d=f84701aae98a424950000000000000009418467bbb64a8edf890201d526c35957d82be3d9588112210f4768db4008d436865636b207061796c6f616401018a4d4e5400000000000000',
            deeplink.generate()
        )

    def test_dataonly_with_payload(self):
        tx = MinterSendCoinTx(
            coin='BIP', to='Mx18467bbb64a8edf890201d526c35957d82be3d95',
            value=1.23456789, nonce=1, gas_coin='MNT', gas_price=1,
            payload='Hello World'
        )
        deeplink = MinterDeeplink(tx=tx)
        deeplink.nonce = ''
        deeplink.gas_coin = ''
        deeplink.gas_price = ''

        self.assertEqual(
            MinterDeeplink.BASE_URL + '?d=f83b01aae98a424950000000000000009418467bbb64a8edf890201d526c35957d82be3d9588112210f4768db4008b48656c6c6f20576f726c64808080',
            deeplink.generate()
        )

    def test_dataonly(self):
        tx = MinterSendCoinTx(
            coin='BIP', to='Mx18467bbb64a8edf890201d526c35957d82be3d95',
            value=1.23456789, nonce=1, gas_coin='MNT', gas_price=1,
            payload='Hello World'
        )
        deeplink = MinterDeeplink(tx=tx, data_only=True)

        self.assertEqual(
            MinterDeeplink.BASE_URL + '?d=f001aae98a424950000000000000009418467bbb64a8edf890201d526c35957d82be3d9588112210f4768db40080808080',
            deeplink.generate()
        )
