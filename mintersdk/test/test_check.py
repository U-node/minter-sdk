import unittest

from mintersdk.sdk.check import MinterCheck
from mintersdk.sdk.transactions import MinterTx


class TestMinterCheck(unittest.TestCase):

    def setUp(self):
        self.PRIVATE_KEY = '64e27afaab363f21eec05291084367f6f1297a7b280d69d672febecda94a09ea'
        self.ADDRESS = 'Mxa7bc33954f1ce855ed1a8c768fdd32ed927def47'
        self.PASSPHRASE = 'pass'
        self.VALID_CHECK = 'Mcf8ae8334383002830f423f8a4d4e5400000000000000888ac7230489e800008a4d4e5400000000000000b841497c5f3e6fc182fd1a791522a9ef7576710bdfbc86fdbf165476ef220e89f9ff1380f93f2d9a2f92fdab0edc1e2605cc2c69b707cd404b2cb1522b7aba4defd5001ba083c9945169f0a7bbe596973b32dc887608780580b1d3bc7b188bedb3bd385594a047b2d5345946ed5498f5bee713f86276aac046a5fef820beaee77a9b6f9bc1df'
        self.VALID_PROOF = 'da021d4f84728e0d3d312a18ec84c21768e0caa12a53cb0a1452771f72b0d1a91770ae139fd6c23bcf8cec50f5f2e733eabb8482cf29ee540e56c6639aac469600'
        self.CHECK = MinterCheck(
            nonce=480,
            due_block=999999,
            coin='MNT',
            value=10,
            passphrase=self.PASSPHRASE,
            chain_id=MinterTx.TESTNET_CHAIN_ID,
            gas_coin='MNT'
        )

    def test_check(self):
        check = self.CHECK.sign(self.PRIVATE_KEY)

        self.assertEqual(check, self.VALID_CHECK)

    def test_proof(self):
        proof = MinterCheck.proof(
            address=self.ADDRESS,
            passphrase=self.PASSPHRASE
        )

        self.assertEqual(proof, self.VALID_PROOF)

    def test_fromraw(self):
        check = MinterCheck.from_raw(rawcheck=self.VALID_CHECK)

        self.assertEqual(
            check.owner,
            'Mxce931863b9c94a526d94acd8090c1c5955a6eb4b'
        )
        self.assertEqual(check.gas_coin, self.CHECK.gas_coin)
