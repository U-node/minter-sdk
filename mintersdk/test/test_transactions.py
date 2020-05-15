import unittest
import base64
import decimal

from mintersdk.sdk.transactions import (
    MinterTx, MinterDelegateTx, MinterSendCoinTx, MinterBuyCoinTx,
    MinterCreateCoinTx, MinterDeclareCandidacyTx, MinterEditCandidateTx,
    MinterRedeemCheckTx, MinterSellAllCoinTx, MinterSellCoinTx,
    MinterSetCandidateOffTx, MinterSetCandidateOnTx, MinterUnbondTx,
    MinterMultiSendCoinTx, MinterCreateMultisigTx
)


class TestMinterTx(unittest.TestCase):

    def setUp(self):
        self.SIGNED_TX = 'f8900102018a4d4e540000000000000007b6f5a00eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a438a4d4e5400000000000000888ac7230489e80000808001b845f8431ba01c2c8f702d80cf64da1e9bf1f07a52e2fee8721aebe419aa9f62260a98983f89a07ed297d71d9dc37a57ffe9bb16915dccc703d8c09f30da8aadb9d5dbab8c7da9'
        self.PUBLIC_KEY = 'Mp0eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a43'
        self.TX_FROM = 'Mx9f7fd953c2c69044b901426831ed03ee0bd0597a'
        self.TX_TYPE = 7
        self.TX_STAKE = 10
        self.TX_PAYLOAD = '🔳'  # 4 bytes
        self.tx = MinterTx.from_raw(self.SIGNED_TX)

    def test_instance(self):
        self.assertIsInstance(self.tx, MinterDelegateTx)

    def test_public_key(self):
        self.assertEqual(self.tx.pub_key, self.PUBLIC_KEY)

    def test_from_mx(self):
        self.assertEqual(self.tx.from_mx, self.TX_FROM)

    def test_type(self):
        self.assertEqual(self.tx.type, self.TX_TYPE)

    def test_stake(self):
        self.assertEqual(self.tx.stake, self.TX_STAKE)


class TestMinterBuyCoinTx(unittest.TestCase):

    def setUp(self):
        self.FROM = 'Mx31e61a05adbd13c6b625262704bc305bf7725026'
        self.PRIVATE_KEY = '07bc17abdcee8b971bb8723e36fe9d2523306d5ab2d683631693238e0f9df142'
        self.SIGNED_TX = 'f8830102018a4d4e540000000000000004a9e88a54455354000000000000880de0b6b3a76400008a4d4e5400000000000000880de0b6b3a7640000808001b845f8431ca04ee095a20ca58062a5758e2a6d3941857daa8943b5873c57f111190ca88dbc56a01148bf2fcc721ca353105e4f4a3419bec471d7ae08173f443a28c3ae6d27018a'
        self.TX = MinterBuyCoinTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'coin_to_buy': 'TEST',
            'value_to_buy': 1,
            'coin_to_sell': 'MNT',
            'max_value_to_sell': 1
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterBuyCoinTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.from_mx, self.FROM)
        self.assertEqual(tx.coin_to_buy, self.TX.coin_to_buy)
        self.assertEqual(tx.value_to_buy, self.TX.value_to_buy)
        self.assertEqual(tx.coin_to_sell, self.TX.coin_to_sell)
        self.assertEqual(tx.max_value_to_sell, self.TX.max_value_to_sell)


class TestMinterCreateCoinTx(unittest.TestCase):

    def setUp(self):
        self.FROM = 'Mx31e61a05adbd13c6b625262704bc305bf7725026'
        self.PRIVATE_KEY = '07bc17abdcee8b971bb8723e36fe9d2523306d5ab2d683631693238e0f9df142'
        self.SIGNED_TX = 'f88f0102018a4d4e540000000000000005b5f48a535550455220544553548a5350525445535400000089056bc75e2d63100000888ac7230489e800000a893635c9adc5dea00000808001b845f8431ca0ccfabd9283d27cf7978bca378e0cc7dc69a39ff3bdc56707fa2d552655f9290da0226057221cbaef35696c9315cd29e783d3c66d842d0a3948a922abb42ca0dabe'
        self.TX = MinterCreateCoinTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'name': 'SUPER TEST',
            'symbol': 'SPRTEST',
            'initial_amount': 100,
            'initial_reserve': 10,
            'crr': 10,
            'max_supply': 1000
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterCreateCoinTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.from_mx, self.FROM)
        self.assertEqual(tx.name, self.TX.name)
        self.assertEqual(tx.symbol, self.TX.symbol)
        self.assertEqual(tx.initial_amount, self.TX.initial_amount)
        self.assertEqual(tx.initial_reserve, self.TX.initial_reserve)
        self.assertEqual(tx.crr, self.TX.crr)
        self.assertEqual(tx.max_supply, self.TX.max_supply)


class TestMinterDeclareCandidacyTx(unittest.TestCase):

    def setUp(self):
        self.PRIVATE_KEY = '6e1df6ec69638d152f563c5eca6c13cdb5db4055861efc11ec1cdd578afd96bf'
        self.SIGNED_TX = 'f8a80102018a4d4e540000000000000006b84df84b949f7fd953c2c69044b901426831ed03ee0bd0597aa00eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a430a8a4d4e5400000000000000884563918244f40000808001b845f8431ca0c379230cbe09103b31983402c9138ad29d839bcecee70e11ac9bf5cfe70850d9a06c92bfb9a627bfaefc3ad46fc60ff1fdc42efe0e8805d57f20795a403c91e8bd'
        self.TX = MinterDeclareCandidacyTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'address': 'Mx9f7fd953c2c69044b901426831ed03ee0bd0597a',
            'pub_key': 'Mp0eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a43',
            'commission': 10,
            'coin': 'MNT',
            'stake': 5
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterDeclareCandidacyTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.from_mx, self.TX.address)
        self.assertEqual(tx.address, self.TX.address)
        self.assertEqual(tx.pub_key, self.TX.pub_key)
        self.assertEqual(tx.commission, self.TX.commission)
        self.assertEqual(tx.coin, self.TX.coin)
        self.assertEqual(tx.stake, self.TX.stake)


class TestMinterDelegateTx(unittest.TestCase):

    def setUp(self):
        self.PRIVATE_KEY = '6e1df6ec69638d152f563c5eca6c13cdb5db4055861efc11ec1cdd578afd96bf'
        self.PUBLIC_KEY = 'Mp0eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a43'
        self.SIGNED_TX = 'f8900102018a4d4e540000000000000007b6f5a00eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a438a4d4e5400000000000000888ac7230489e80000808001b845f8431ba01c2c8f702d80cf64da1e9bf1f07a52e2fee8721aebe419aa9f62260a98983f89a07ed297d71d9dc37a57ffe9bb16915dccc703d8c09f30da8aadb9d5dbab8c7da9'

        self.TX = MinterDelegateTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'pub_key': self.PUBLIC_KEY,
            'coin': 'MNT',
            'stake': 10
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterDelegateTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.pub_key, self.PUBLIC_KEY)
        self.assertEqual(tx.coin, self.TX.coin)
        self.assertEqual(tx.stake, self.TX.stake)


class TestMinterRedeemCheckTx(unittest.TestCase):

    def setUp(self):
        self.PRIVATE_KEY = '05ddcd4e6f7d248ed1388f0091fe345bf9bf4fc2390384e26005e7675c98b3c1'
        self.SIGNED_TX = 'f9013f0102018a4d4e540000000000000009b8e4f8e2b89df89b01830f423f8a4d4e5400000000000000843b9aca00b8419b3beac2c6ad88a8bd54d24912754bb820e58345731cb1b9bc0885ee74f9e50a58a80aa990a29c98b05541b266af99d3825bb1e5ed4e540c6e2f7c9b40af9ecc011ca00f7ba6d0aa47d74274b960fba02be03158d0374b978dcaa5f56fc7cf1754f821a019a829a3b7bba2fc290f5c96e469851a3876376d6a6a4df937327b3a5e9e8297b841da021d4f84728e0d3d312a18ec84c21768e0caa12a53cb0a1452771f72b0d1a91770ae139fd6c23bcf8cec50f5f2e733eabb8482cf29ee540e56c6639aac469600808001b845f8431ba009493b3296a085a27f2bc015ad5c1cc644ba21bdce1b78a49e987227f24a87a3a07187da48b6ea528d372ed33923f5d74011f56cc2db3cab2cf5b4bbab97990373'
        self.TX = MinterRedeemCheckTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'check': 'Mcf89b01830f423f8a4d4e5400000000000000843b9aca00b8419b3beac2c6ad88a8bd54d24912754bb820e58345731cb1b9bc0885ee74f9e50a58a80aa990a29c98b05541b266af99d3825bb1e5ed4e540c6e2f7c9b40af9ecc011ca00f7ba6d0aa47d74274b960fba02be03158d0374b978dcaa5f56fc7cf1754f821a019a829a3b7bba2fc290f5c96e469851a3876376d6a6a4df937327b3a5e9e8297',
            'proof': 'da021d4f84728e0d3d312a18ec84c21768e0caa12a53cb0a1452771f72b0d1a91770ae139fd6c23bcf8cec50f5f2e733eabb8482cf29ee540e56c6639aac469600'
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterRedeemCheckTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.check, self.TX.check)
        self.assertEqual(tx.proof, self.TX.proof)


class TestMinterSellAllCoinTx(unittest.TestCase):

    def setUp(self):
        self.FROM = 'Mx31e61a05adbd13c6b625262704bc305bf7725026'
        self.PRIVATE_KEY = '07bc17abdcee8b971bb8723e36fe9d2523306d5ab2d683631693238e0f9df142'
        self.SIGNED_TX = 'f87a0102018a4d4e540000000000000003a0df8a4d4e54000000000000008a54455354000000000000880de0b6b3a7640000808001b845f8431ca0b10794a196b6ad2f94e6162613ca9538429dd49ca493594ba9d99f80d2499765a03c1d78e9e04f57336691e8812a16faccb00bf92ac817ab61cd9bf001e9380d47'
        self.TX = MinterSellAllCoinTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'coin_to_sell': 'MNT',
            'coin_to_buy': 'TEST',
            'min_value_to_buy': 1
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterSellAllCoinTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.from_mx, self.FROM)
        self.assertEqual(tx.coin_to_sell, self.TX.coin_to_sell)
        self.assertEqual(tx.coin_to_buy, self.TX.coin_to_buy)
        self.assertEqual(tx.min_value_to_buy, self.TX.min_value_to_buy)


class TestMinterSellCoinTx(unittest.TestCase):

    def setUp(self):
        self.FROM = 'Mx31e61a05adbd13c6b625262704bc305bf7725026'
        self.PRIVATE_KEY = '07bc17abdcee8b971bb8723e36fe9d2523306d5ab2d683631693238e0f9df142'
        self.SIGNED_TX = 'f8830102018a4d4e540000000000000002a9e88a4d4e5400000000000000880de0b6b3a76400008a54455354000000000000880de0b6b3a7640000808001b845f8431ba0e34be907a18acb5a1aed263ef419f32f5adc6e772b92f949906b497bba557df3a0291d7704980994f7a6f5950ca84720746b5928f21c3cfc5a5fbca2a9f4d35db0'
        self.TX = MinterSellCoinTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'coin_to_sell': 'MNT',
            'value_to_sell': 1,
            'coin_to_buy': 'TEST',
            'min_value_to_buy': 1
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterSellCoinTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.from_mx, self.FROM)
        self.assertEqual(tx.coin_to_sell, self.TX.coin_to_sell)
        self.assertEqual(tx.value_to_sell, self.TX.value_to_sell)
        self.assertEqual(tx.coin_to_buy, self.TX.coin_to_buy)
        self.assertEqual(tx.min_value_to_buy, self.TX.min_value_to_buy)


class TestMinterSendTx(unittest.TestCase):

    def setUp(self):
        self.PRIVATE_KEY = '07bc17abdcee8b971bb8723e36fe9d2523306d5ab2d683631693238e0f9df142'
        self.TO = 'Mx1b685a7c1e78726c48f619c497a07ed75fe00483'
        self.FROM = 'Mx31e61a05adbd13c6b625262704bc305bf7725026'
        self.SIGNED_TX = 'f8840102018a4d4e540000000000000001aae98a4d4e5400000000000000941b685a7c1e78726c48f619c497a07ed75fe00483880de0b6b3a7640000808001b845f8431ca01f36e51600baa1d89d2bee64def9ac5d88c518cdefe45e3de66a3cf9fe410de4a01bc2228dc419a97ded0efe6848de906fbe6c659092167ef0e7dcb8d15024123a'
        self.TX = MinterSendCoinTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'to': self.TO,
            'coin': 'MNT',
            'value': 1
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterSendCoinTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(self.SIGNED_TX)

        self.assertEqual(tx.from_mx, self.FROM)
        self.assertEqual(tx.to, self.TX.to)
        self.assertEqual(tx.coin, self.TX.coin)
        self.assertEqual(tx.value, self.TX.value)


class TestMinterSetCandidateOffTx(unittest.TestCase):

    def setUp(self):
        self.PRIVATE_KEY = '05ddcd4e6f7d248ed1388f0091fe345bf9bf4fc2390384e26005e7675c98b3c1'
        self.SIGNED_TX = 'f87c0102018a4d4e54000000000000000ba2e1a00eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a43808001b845f8431ca02ac45817f167c34b55b8afa0b6d9692be28e2aa41dd28a134663d1f5bebb5ad8a06d5f161a625701d506db20c497d24e9939c2e342a6ff7d724cb1962267bd4ba5'
        self.TX = MinterSetCandidateOffTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'pub_key': 'Mp0eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a43'
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterSetCandidateOffTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.pub_key, self.TX.pub_key)


class TestMinterSetCandidateOnTx(unittest.TestCase):

    def setUp(self):
        self.PRIVATE_KEY = '05ddcd4e6f7d248ed1388f0091fe345bf9bf4fc2390384e26005e7675c98b3c1'
        self.SIGNED_TX = 'f87c0102018a4d4e54000000000000000aa2e1a00eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a43808001b845f8431ba0095aed433171fe5ac385ccd299507bdcad3dd2269794fd0d14d4f58327ddc87ea046ec7e4f8f9b477a1255485f36e0567e62283723ecc5a0bd1e5d201e53e85245'
        self.TX = MinterSetCandidateOnTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'pub_key': 'Mp0eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a43'
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterSetCandidateOnTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.pub_key, self.TX.pub_key)


class TestMinterUnbondTx(unittest.TestCase):

    def setUp(self):
        self.PRIVATE_KEY = '6e1df6ec69638d152f563c5eca6c13cdb5db4055861efc11ec1cdd578afd96bf'
        self.SIGNED_TX = 'f88f0102018a4d4e540000000000000008b6f5a00eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a438a4d4e5400000000000000888ac7230489e80000808001b844f8421ca0ff5766c85847b37a276f3f9d027fb7c99745920fa395c7bd399cedd8265c5e1d9f791bcdfe4d1bc1e73ada7bf833103c828f22d83189dad2b22ad28a54aacf2a'
        self.TX = MinterUnbondTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'pub_key': 'Mp0eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a43',
            'coin': 'MNT',
            'value': 10
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterUnbondTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.pub_key, self.TX.pub_key)
        self.assertEqual(tx.coin, self.TX.coin)
        self.assertEqual(tx.value, self.TX.value)


class TestMinterEditCandidateTx(unittest.TestCase):

    def setUp(self):
        self.FROM = 'Mxa879439b0a29ecc7c5a0afe54b9eb3c22dbde8d9'
        self.PRIVATE_KEY = 'a3fb55450f53dbbf4f2494280188f7f0cd51a7b51ec27ed49ed364d920e326ba'
        self.SIGNED_TX = 'f8a80102018a4d4e54000000000000000eb84df84ba04ae1ee73e6136c85b0ca933a9a1347758a334885f10b3238398a67ac2eb153b89489e5dc185e6bab772ac8e00cf3fb3f4cb0931c4794e731fcddd37bb6e72286597d22516c8ba3ddffa0808001b845f8431ca0421470f27f78231b669c1bf1fcc56168954d64fbb7dc3ff021bab01311fab6eaa075e86365d98c87e806fcbc5c542792f569e19d8ae7af671d9ba4679acc86d35e'
        self.TX = MinterEditCandidateTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'pub_key': 'Mp4ae1ee73e6136c85b0ca933a9a1347758a334885f10b3238398a67ac2eb153b8',
            'reward_address': 'Mx89e5dc185e6bab772ac8e00cf3fb3f4cb0931c47',
            'owner_address': 'Mxe731fcddd37bb6e72286597d22516c8ba3ddffa0'
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterEditCandidateTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.from_mx, self.FROM)
        self.assertEqual(tx.pub_key, self.TX.pub_key)
        self.assertEqual(tx.reward_address, self.TX.reward_address)
        self.assertEqual(tx.owner_address, self.TX.owner_address)


class TestMinterMultiSendCoinTx(unittest.TestCase):

    def setUp(self):
        self.FROM = 'Mx31e61a05adbd13c6b625262704bc305bf7725026'
        self.PRIVATE_KEY = '07bc17abdcee8b971bb8723e36fe9d2523306d5ab2d683631693238e0f9df142'
        self.SIGNED_TX = 'f8b30102018a4d4e54000000000000000db858f856f854e98a4d4e540000000000000094fe60014a6e9ac91618f5d1cab3fd58cded61ee9988016345785d8a0000e98a4d4e540000000000000094ddab6281766ad86497741ff91b6b48fe85012e3c8802c68af0bb140000808001b845f8431ca0b15dcf2e013df1a2aea02e36a17af266d8ee129cdcb3e881d15b70c9457e7571a0226af7bdaca9d42d6774c100b22e0c7ba4ec8dd664d17986318e905613013283'
        self.TX = MinterMultiSendCoinTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'txs': [
                {
                    'coin': 'MNT',
                    'to': 'Mxfe60014a6e9ac91618f5d1cab3fd58cded61ee99',
                    'value': decimal.Decimal('0.1')
                },
                {
                    'coin': 'MNT',
                    'to': 'Mxddab6281766ad86497741ff91b6b48fe85012e3c',
                    'value': decimal.Decimal('0.2')
                }
            ]
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterMultiSendCoinTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.from_mx, self.FROM)
        self.assertEqual(tx.txs, self.TX.txs)

    def test_sign_with_signature(self):
        self.TX.signature_type = MinterTx.SIGNATURE_SINGLE_TYPE
        signature = self.TX.generate_signature(self.PRIVATE_KEY)
        self.TX.sign(signature=signature)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)


class TestTxFees(unittest.TestCase):

    def setUp(self):
        self.TO = 'Mx31e61a05adbd13c6b625262704bc305bf7725026'
        self.PRIVATE_KEY = '07bc17abdcee8b971bb8723e36fe9d2523306d5ab2d683631693238e0f9df142'
        self.TX_PAYLOAD_UTF = '🔳'  # 4 bytes
        self.EXPECTED_SEND_COIN_FEE = 18000000000000000

        self.MULTISEND_RECIPIENTS = [
            {
                'coin': 'MNT',
                'to': 'Mxfe60014a6e9ac91618f5d1cab3fd58cded61ee99',
                'value': 0.1
            },
            {
                'coin': 'MNT',
                'to': 'Mxddab6281766ad86497741ff91b6b48fe85012e3c',
                'value': 0.2
            }
        ]
        self.EXPECTED_MULTISEND_FEE = 15000000000000000

    def test_payload_fee(self):
        tx = MinterSendCoinTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'to': self.TO,
            'coin': 'MNT',
            'value': 1,
            'payload': self.TX_PAYLOAD_UTF
        })
        tx.sign(self.PRIVATE_KEY)
        actual_fee = tx.get_fee()
        self.assertEqual(self.EXPECTED_SEND_COIN_FEE, actual_fee)

    def test_multisend_fee(self):
        tx = MinterMultiSendCoinTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'txs': self.MULTISEND_RECIPIENTS
        })
        tx.sign(self.PRIVATE_KEY)
        actual_fee = tx.get_fee()
        self.assertEqual(self.EXPECTED_MULTISEND_FEE, actual_fee)


class TestMinterSendMultisigTx(unittest.TestCase):

    def setUp(self):
        self.PRIVATE_KEYS = [
            'b354c3d1d456d5a1ddd65ca05fd710117701ec69d82dac1858986049a0385af9',
            '38b7dfb77426247aed6081f769ed8f62aaec2ee2b38336110ac4f7484478dccb',
            '94c0915734f92dd66acfdc48f82b1d0b208efd544fe763386160ec30c968b4af'
        ]
        self.TO = 'Mxd82558ea00eb81d35f2654953598f5d51737d31d'
        self.FROM = 'Mxdb4f4b6942cb927e8d7e3a1f602d0f1fb43b5bd2'
        self.SIGNED_TX = 'f901270102018a4d4e540000000000000001aae98a4d4e540000000000000094d82558ea00eb81d35f2654953598f5d51737d31d880de0b6b3a7640000808002b8e8f8e694db4f4b6942cb927e8d7e3a1f602d0f1fb43b5bd2f8cff8431ca0a116e33d2fea86a213577fc9dae16a7e4cadb375499f378b33cddd1d4113b6c1a021ee1e9eb61bbd24233a0967e1c745ab23001cf8816bb217d01ed4595c6cb2cdf8431ca0f7f9c7a6734ab2db210356161f2d012aa9936ee506d88d8d0cba15ad6c84f8a7a04b71b87cbbe7905942de839211daa984325a15bdeca6eea75e5d0f28f9aaeef8f8431ba0d8c640d7605034eefc8870a6a3d1c22e2f589a9319288342632b1c4e6ce35128a055fe3f93f31044033fe7b07963d547ac50bccaac38a057ce61665374c72fb454'
        self.TX = MinterSendCoinTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'to': self.TO,
            'coin': 'MNT',
            'value': 1
        })

    def test_valid_tx(self):
        """
        Is tx instance of needed TX class.
        """

        self.assertIsInstance(self.TX, MinterSendCoinTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        self.TX.sign(private_key=self.PRIVATE_KEYS, ms_address=self.FROM)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(self.SIGNED_TX)

        self.assertEqual(tx.from_mx, self.FROM)
        self.assertEqual(tx.to, self.TX.to)
        self.assertEqual(tx.coin, self.TX.coin)
        self.assertEqual(tx.value, self.TX.value)

    def test_add_signature(self):
        # Sign tx with 2 of 3 private keys
        self.TX.sign(private_key=self.PRIVATE_KEYS[:2], ms_address=self.FROM)
        # Add signature by 3rd private key
        self.TX = MinterTx.add_signature(self.TX.signed_tx, self.PRIVATE_KEYS[2])

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_signature(self):
        # Set signature type for transaction
        self.TX.signature_type = MinterTx.SIGNATURE_MULTI_TYPE

        # Generate signatures
        signatures = []
        for pk in self.PRIVATE_KEYS:
            signature = self.TX.generate_signature(private_key=pk)
            signatures.append(signature)

        # Sign transaction with signatures
        self.TX.sign(signature=signatures, ms_address=self.FROM)

        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_sign_with_pk_and_signature(self):
        # Set signature type for transaction
        self.TX.signature_type = MinterTx.SIGNATURE_MULTI_TYPE

        # Generate 1 signature
        signatures = []
        for pk in self.PRIVATE_KEYS:
            signatures.append(self.TX.generate_signature(private_key=pk))

        # Sign transaction with pks and signature
        self.TX.sign(private_key=self.PRIVATE_KEYS[:2], signature=signatures[2], ms_address=self.FROM)
        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

        self.TX.sign(private_key=self.PRIVATE_KEYS[0], signature=signatures[1:], ms_address=self.FROM)
        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)


class TestPayloadsFromRaw(unittest.TestCase):
    def setUp(self):
        self.TO = 'Mxd82558ea00eb81d35f2654953598f5d51737d31d'
        self.FROM = 'Mx31e61a05adbd13c6b625262704bc305bf7725026'
        self.PK = '07bc17abdcee8b971bb8723e36fe9d2523306d5ab2d683631693238e0f9df142'
        self.TX = MinterSendCoinTx(
            nonce=1, gas_coin='mnt', to=self.TO, coin='mnt', value=1
        )
        self.TX_DECODED = None

    def sign_and_decode(self, payload):
        self.TX.payload = payload
        self.TX.sign(private_key=self.PK)
        self.TX_DECODED = MinterTx.from_raw(self.TX.signed_tx)

    def test_hex_like(self):
        payload = 'fff'
        self.sign_and_decode(payload)

        self.assertEqual(payload, self.TX_DECODED.payload)
        self.assertEqual(self.FROM, self.TX_DECODED.from_mx)

    def test_str_bytes(self):
        payload = '🔳'
        self.sign_and_decode(payload)

        self.assertEqual(payload, self.TX_DECODED.payload)
        self.assertEqual(self.FROM, self.TX_DECODED.from_mx)

    def test_raw_bytes(self):
        payload = b'\xff\xff\xff'
        self.sign_and_decode(payload)

        self.assertEqual(payload, self.TX_DECODED.payload)
        self.assertEqual(self.FROM, self.TX_DECODED.from_mx)


class TestFromBase64(unittest.TestCase):
    def setUp(self):
        self.B64_TXS = [
            '+Hw8AQGKQklQAAAAAAAAAAKi4YpPTEJJVFgAAAAAiQHluPqP4qwAAIpMRU1PTgAAAAAAgICAAbhF+EMboPtT5w1Brh5BO66qs75e1sOj9Ka4KfxGQDOFsQssgNn/oAeDnTkaMj685tdWvWa6rUmViaCB+KerPBDHUE7O731j',
            '+H+DBJaHAQGKQklQAAAAAAAAAAGi4YpCSVAAAAAAAAAAlJXK8ve/qfgqz5QEbX52KCQKOQ/bgICAAbhF+EMcoFVh1TOlkwUHmSpEvOQprRnZgnpSeIFxXn15fApbl28qoFR5GhbH34BiCmpwqY+Qs4xI5DjfE9PNfVYEZ7axgyvc',
            '+IeCGxkBAYpCSVAAAAAAAAAAAavqikNPTlNVTEdBTUWUm7rikGga0Jtdjuse5KRJp2SOn8WJAaBVaQ2duAAAgIABuEX4QxygBQd9EAxqcsKigdqsvCEVA5GapLPxdlbZ/DYkC3RXpYOgJ2QuKIW1U/yrTVec56v06V42VwaO2VRqGvuJVLkojvU=',
            '+HqCMGYBAYpCSVAAAAAAAAAAA57dikJJUAAAAAAAAACKQ0VOVEFVUlVTAIZa8xB6QACAgAG4RfhDG6A+PinAE4fNMpPwC8U8/DbHNSIERcWDE9rridQ1DyECAaBiGkXNmAgUnYK2VjJjMLJGWLN4T3jz/2KylTFZqXNM5Q==',
            '+H6CBYcBAYpCSVAAAAAAAAAAAqLhikJJUAAAAAAAAACJARWORgkT0AAAilRBUFRBUAAAAACAgIABuEX4Qxug8tXe0wJ61FNJq+p/KEVsTE044Cq5mqtnD55xyUM2niigCPjkKq+K5Rabeghgyf7+zxjOhykruz0dQOoZR5GzbZ8=',
            '+JKB2AEBikJJUAAAAAAAAAAHt/agd/cYNBCOm15lI3o5JjYxtPmanVhDehOFyTDBPuHU4qaKT05MWTEAAAAAAIm+S9/Lh9P4ZoqAgAG4RfhDG6AVkWCf6F/LQlIUjBFQFCcfAgWxhRBTs7ZdLDLOaUQntaB/C/kHw/fRLDH/ZMM5hdZpx87pZZfTRTuQ6Peda7ParA==',
            '+IRVAQGKQklQAAAAAAAAAAGq6YpCSVAAAAAAAAAAlG3tXZ5JAX3uqMMYO7aKsxx9JGTxiIrHIwSJ6AAAgIABuEX4QxugLtA0N8YgapJtAF4/oq4mgnDeTAFy64tAfhlY2POh4fmgTB1pdMhcBzpSiPqUTVPTCn+xwAxpTD8eQsV5+ZWEM40=',
            '+JKCTDIBAYpCSVAAAAAAAAAAB7b1oGKbVSjwnRx0qD0YQU8uQmPhSFDEej+sP4VfIAERERERikJJUAAAAAAAAACIRWORgkT0AACAgAG4RfhDG6BbXtr6FKf4Ifdlji3nCSqUQ3OEfReYBUfa71+zNb0wh6AEZSWMY7CGXvh3Rqjjiam9IT3NL7gvI/wrqxSrFkxj/g==',
            '+JOCB6IBAYpCSVAAAAAAAAAAB7f2oGKbVSjwnRx0qD0YQU8uQmPhSFDEej+sP4VfIAERERERikJJUAAAAAAAAACJFa8deLWMQAAAgIABuEX4Qxyg3MYUWNZZPy1k4ikM97HJ7RJuLCHyteqUymPVQ+r+qJygcN2yKmUK9adEaqjQRNEHesgRE+dAlamHu2Bd7OE4zwI=',
            '+JOCAZIBAYpCSVAAAAAAAAAAB7f2oGKbVSjwnRx0qD0YQU8uQmPhSFDEej+sP4VfIAERERERikJJUAAAAAAAAACJBbEq76+oBAAAgIABuEX4QxygLl0jQ98RtdXCkIKDYce9OD11tpA4kmAtPLXIGkeycAKgGRsYDVVx+SD98N4zKByD2H+w0yToFuZk8gN2PtWVNpQ=',
            '+IQJAQGKQklQAAAAAAAAAAGq6YpCSVAAAAAAAAAAlJ9/UFrwbYh8dflHt3kRDT99fUG/iJNP9bP1XNAAgIABuEX4QxugOu3JcCce9OO5rpWDVsQpGk+gwTLbt3p8qu2YM7Tg1UGgF8Ez00im24HKFlJM2DWoUSJ3G1BjzREg1AGG6dP1s1s=',
            '+H6CB1UBAYpCSVAAAAAAAAAAAqLhikJJUAAAAAAAAACJEENWGogpMAAAikNFTlRBVVJVUwCAgIABuEX4QxugfLaJkvWttDTqA9EelJ+9RQ8anWwngbIkeOuQydh0RI2gB0JC+oxPrSmB8dZmazeh3ot2Ff6bE2czGfwgPu7ZpCg=',
            '+PaCAw8BAYpCSVAAAAAAAAAAAavqikJJUAAAAAAAAACUvW+bnucw5qCqmK4SHaLeJ1gp4YSJYadP9azWWcAAuG5CaXBleC5uZXQgLSBTdWNjZXNzIEJpcCB3aXRoZHJhd2FsICMxMzczOC4gT3VyIGN1cnJlbnQgZXhjaGFuZ2UgcmF0ZXMgZm9yIDEgQklQOiAwLjAxNDckIC8gMC4wMTUzJC4gRm9sbG93IHVzLoABuEX4Qxug7zYujmw36ehtj+scZxn+Zlpj3NrtUp924DwBS9+hkJagQtz8zLrB4jgzLnFtDv1F0t1gKQnpU6PyTYGuicMMRe0=',
            '+H+DBJaLAQGKQklQAAAAAAAAAAGi4YpCSVAAAAAAAAAAlJXK8ve/qfgqz5QEbX52KCQKOQ/bgICAAbhF+EMboKGqlP2cC2tqtsnntOBRAg9XNsVBBb5wLBjCPlp5RuBaoDLYDXbDwKQz/ONyYoDV9AUI0C7wCME+T/gGeR1BEdCu',
            '+JOCARABAYpCSVAAAAAAAAAAB7f2oEiBrRZ8pftYhjIoQfmS1ortiU/8tYq8CA6K07FW8QRbikJJUAAAAAAAAACJA9NIdC2o2QDmgIABuEX4QxugGdqhQ+dkzUft+Pc5/A0TYUXcZLGDLA8C/5Q2GzNhRoygaAxGtwGHh9VCrOUVsUCvxOyMSZkMqIbC2i7LVKNY6qU=',
            '+IQJAQGKQklQAAAAAAAAAAGq6YpCSVAAAAAAAAAAlJ9/UFrwbYh8dflHt3kRDT99fUG/iJb2P7XLwAAAgIABuEX4QxygHiZ64dA9EZbsmjLMtDWPvs/Sn4vLjTeCjAizxgEyFhegG9HDwfYDX249KO/kIVXnOsUUBTA1u6KvsImtRTYwyA0=',
            '+H6CB1YBAYpCSVAAAAAAAAAAAqLhikJJUAAAAAAAAACJEENWGogpMAAAik9ORUJJUAAAAACAgIABuEX4Qxug81K8K87BiQpmawv8wBT/8wJA7xexSiStKlH+ijGE+/agCOLB7aqTVi62WHw2BgRBIlYMICc3LOSqsWE6lFku3Ew=',
            '+IaCAwQBAYpCSVAAAAAAAAAAAarpikZBTENPTgAAAACUhfwWxlBErQ8ZAvfDq2FnB0UsxeaIDeC2s6dkAACAgAG4RfhDG6C1m77cTSA1qllKv8FOW3/BaIO3lVQtrVclDUd5ay3NpaBPHg/nkVgAfN63rRKBYiNZBb+4sa4tVjSLlL2v6yVB5w==',
            '+IMrAQGKQklQAAAAAAAAAAKp6IpCSVAAAAAAAAAAiAr2pNB8jwAAikVDT05BAAAAAACITCl3L4h8OpGAgAG4RfhDG6DX7yY6y9xkV640fWT9EMcIH/WDrPu3Y4hX9zpESaijPKBVP7Z56G2J1urB3QZq9cl7AaYbE7EZeAMWsCsidQGXvg==',
            '+IUBAQGKQklQAAAAAAAAAAGr6opCSVAAAAAAAAAAlK/SZxtm+xqSGATRe5jj+eCa+bhmiXPriL12u+CcAICAAbhF+EMboJioZmk/kgs9vAcJcvM8VwmoRuws0s02eMT9yMqNr5s7oBk5m7YSzSIKDjRQYRjyaktm+zMQI4JluYnQVSOpbVkt'
        ]

    @staticmethod
    def base64ToHex(b64str):
        b64_bytes = b64str.encode()
        tx_bytes = base64.b64decode(b64_bytes)

        return tx_bytes.hex()

    def test_txs(self):
        for index, b64_tx in enumerate(self.B64_TXS):
            try:
                raw_tx = self.base64ToHex(b64_tx)
                MinterTx.from_raw(raw_tx)
            except Exception as e:
                self.fail(f'Tx #{index} from base64 failed: {e.__str__()}')


class TestMinterCreateMultisigTx(unittest.TestCase):

    def setUp(self):
        self.FROM = 'Mx3e4d56e776ff42c023b1ec99a7486b592a654981'
        self.PRIVATE_KEY = 'bc3503cae8c8561df5eadc4a9eda21d32c252a6c94cfae55b5310bf6085c8582'
        self.SIGNED_TX = 'f8a30102018a4d4e54000000000000000cb848f84607c3010305f83f94ee81347211c72524338f9680072af9074433314394ee81347211c72524338f9680072af9074433314594ee81347211c72524338f9680072af90744333144808001b845f8431ca094eb41d39e6782f5539615cc66da7073d4283893f0b3ee2b2f36aee1eaeb7c57a037f90ffdb45eb9b6f4cf301b48e73a6a81df8182e605b656a52057537d264ab4'
        self.TX = MinterCreateMultisigTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'threshold': 7,
            'weights': [1, 3, 5],
            'addresses': [
                'Mxee81347211c72524338f9680072af90744333143',
                'Mxee81347211c72524338f9680072af90744333145',
                'Mxee81347211c72524338f9680072af90744333144'
            ]
        })

    def test_valid_tx(self):
        """ Is tx instance of needed TX class. """
        self.assertIsInstance(self.TX, MinterCreateMultisigTx)

        with self.assertRaisesRegex(ValueError, 'threshold'):
            MinterCreateMultisigTx(
                nonce=1, gas_coin='mnt', threshold=1.1, weights=[1],
                addresses=['Mxee81347211c72524338f9680072af90744333143']
            )

        with self.assertRaisesRegex(ValueError, 'weights'):
            MinterCreateMultisigTx(
                nonce=1, gas_coin='mnt', threshold=1, weights=[0, '1', 1024],
                addresses=['Mxee81347211c72524338f9680072af90744333143']
            )

    def test_sign_tx(self):
        """ Sign transaction and check signed transaction """
        self.TX.sign(self.PRIVATE_KEY)
        self.assertEqual(self.TX.signed_tx, self.SIGNED_TX)

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.from_mx, self.FROM)
        self.assertEqual(tx.threshold, self.TX.threshold)
        self.assertEqual(tx.weights, self.TX.weights)
        self.assertEqual(tx.addresses, self.TX.addresses)


if __name__ == '__main__':
    unittest.main()
