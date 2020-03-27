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
            MinterDeeplink.BASE_URL + '/-EcBqumKQklQAAAAAAAAAJQYRnu7ZKjt-JAgHVJsNZV9gr49lYgRIhD0do20AI1DaGVjayBwYXlsb2FkAQGKTU5UAAAAAAAAAA',
            deeplink.generate()
        )

    def test_data_part_with_payload(self):
        tx = MinterSendCoinTx(
            coin='MNT', to='Mx7633980c000139dd3bd24a3f54e06474fa941e16',
            value=10, nonce=1, gas_coin='ASD', gas_price=1,
            payload='custom message'
        )
        deeplink = MinterDeeplink(tx=tx)
        deeplink.nonce = ''
        deeplink.gas_price = ''

        self.assertEqual(
            MinterDeeplink.BASE_URL + '/-EgBqumKTU5UAAAAAAAAAJR2M5gMAAE53TvSSj9U4GR0-pQeFoiKxyMEiegAAI5jdXN0b20gbWVzc2FnZYCAikFTRAAAAAAAAAA',
            deeplink.generate()
        )

    def test_data_only(self):
        tx = MinterSendCoinTx(
            coin='BIP', to='Mx18467bbb64a8edf890201d526c35957d82be3d95',
            value=1.23456789, nonce=1, gas_coin='MNT', gas_price=1,
            payload='Hello World'
        )
        deeplink = MinterDeeplink(tx=tx, data_only=True)

        self.assertEqual(
            MinterDeeplink.BASE_URL + '/8AGq6YpCSVAAAAAAAAAAlBhGe7tkqO34kCAdUmw1lX2Cvj2ViBEiEPR2jbQAgICAgA',
            deeplink.generate()
        )
