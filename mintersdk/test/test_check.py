import unittest
from mintersdk.sdk.check import MinterCheck
from mintersdk.sdk.transactions import MinterTx


class TestMinterCheck(unittest.TestCase):

    def setUp(self):
        self.PRIVATE_KEY = '64e27afaab363f21eec05291084367f6f1297a7b280d69d672febecda94a09ea'
        self.ADDRESS = 'Mxa7bc33954f1ce855ed1a8c768fdd32ed927def47'
        self.PASSPHRASE = 'pass'
        self.VALID_CHECK = 'Mcf8a38334383002830f423f8a4d4e5400000000000000888ac7230489e80000b841d184caa333fe636288fc68d99dea2c8af5f7db4569a0bb91e03214e7e238f89d2b21f4d2b730ef590fd8de72bd43eb5c6265664df5aa3610ef6c71538d9295ee001ba08bd966fc5a093024a243e62cdc8131969152d21ee9220bc0d95044f54e3dd485a033bc4e03da3ea8a2cd2bd149d16c022ee604298575380db8548b4fd6672a9195'
        self.VALID_PROOF = 'da021d4f84728e0d3d312a18ec84c21768e0caa12a53cb0a1452771f72b0d1a91770ae139fd6c23bcf8cec50f5f2e733eabb8482cf29ee540e56c6639aac469600'
        self.CHECK = MinterCheck(
            nonce=480,
            due_block=999999,
            coin='MNT',
            value=10,
            passphrase=self.PASSPHRASE,
            chain_id=MinterTx.TESTNET_CHAIN_ID
        )

    def test_check(self):
        check = self.CHECK.sign(self.PRIVATE_KEY)

        self.assertEqual(check, self.VALID_CHECK)

    def test_proof(self):
        proof = MinterCheck.proof(address=self.ADDRESS, passphrase=self.PASSPHRASE)

        self.assertEqual(proof, self.VALID_PROOF)

    def test_fromraw(self):
        check = MinterCheck.from_raw(rawcheck=self.VALID_CHECK)

        self.assertEqual(check.owner, 'Mxce931863b9c94a526d94acd8090c1c5955a6eb4b')
