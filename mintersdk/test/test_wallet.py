import unittest

from mintersdk.sdk.wallet import MinterWallet


class TestMinterWallet(unittest.TestCase):

    def setUp(self):
        self.mnemonic = 'slice better asset talent state citizen dry maze base agent source reveal'
        self.private_key = '7ffc6bc08f2d8a0ead1d3f64e6a9862b7695dafceca24f25978341447594aa07'
        self.address = 'Mx5a4c6c7fbd05ff8e5b09818db5ad229852784e01'

    def test_private_key(self):
        wallet = MinterWallet.create(mnemonic=self.mnemonic)
        self.assertEqual(wallet['private_key'], self.private_key)

    def test_address(self):
        wallet = MinterWallet.create(mnemonic=self.mnemonic)
        self.assertEqual(wallet['address'], self.address)

    def test_creation(self):
        for _ in range(250):
            MinterWallet.create()
