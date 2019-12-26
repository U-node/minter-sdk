"""
@author: rymka1989
"""
import unittest
from mintersdk.sdk.transactions import (
    MinterTx, MinterDelegateTx, MinterSendCoinTx, MinterBuyCoinTx,
    MinterCreateCoinTx, MinterDeclareCandidacyTx, MinterEditCandidateTx,
    MinterRedeemCheckTx, MinterSellAllCoinTx, MinterSellCoinTx,
    MinterSetCandidateOffTx, MinterSetCandidateOnTx, MinterUnbondTx,
    MinterMultiSendCoinTx
)


class TestMinterTx(unittest.TestCase):

    def setUp(self):
        self.SIGNED_TX = 'f8900102018a4d4e540000000000000007b6f5a00eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a438a4d4e5400000000000000888ac7230489e80000808001b845f8431ba01c2c8f702d80cf64da1e9bf1f07a52e2fee8721aebe419aa9f62260a98983f89a07ed297d71d9dc37a57ffe9bb16915dccc703d8c09f30da8aadb9d5dbab8c7da9'
        self.PUBLIC_KEY = 'Mp0eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a43'
        self.TX_FROM = 'Mx9f7fd953c2c69044b901426831ed03ee0bd0597a'
        self.TX_TYPE = 7
        self.TX_STAKE = 10
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
        self.SIGNED_TX = 'f8850102018a4d4e540000000000000005abea8a535550455220544553548a5350525445535400000089056bc75e2d63100000888ac7230489e800000a808001b845f8431ca0a0b58787e19d8ef3cbd887936617af5cf069a25a568f838c3d04daf5ad2f6f8ea07660c13ab5017edb87f5b52be4574c8a33a893bac178adec9c262a1408e4f1fe'
        self.TX = MinterCreateCoinTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'name': 'SUPER TEST',
            'symbol': 'SPRTEST',
            'initial_amount': 100,
            'initial_reserve': 10,
            'crr': 10
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

    def test_from_raw(self):
        tx = MinterTx.from_raw(raw_tx=self.SIGNED_TX)

        self.assertEqual(tx.from_mx, self.FROM)
        self.assertEqual(tx.name, self.TX.name)
        self.assertEqual(tx.symbol, self.TX.symbol)
        self.assertEqual(tx.initial_amount, self.TX.initial_amount)
        self.assertEqual(tx.initial_reserve, self.TX.initial_reserve)
        self.assertEqual(tx.crr, self.TX.crr)


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
                    'value': 0.1
                },
                {
                    'coin': 'MNT',
                    'to': 'Mxddab6281766ad86497741ff91b6b48fe85012e3c',
                    'value': 0.2
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


if __name__ == '__main__':
    unittest.main()
