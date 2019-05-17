'''
Created on 31 окт. 2018 г.

@author: Roman
'''
import unittest
from mintersdk.sdk.transactions import MinterTx, MinterDelegateTx, MinterSendCoinTx


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


class TestMinterDelegateTx(unittest.TestCase):

    def setUp(self):
        self.PRIVATE_KEY = '6e1df6ec69638d152f563c5eca6c13cdb5db4055861efc11ec1cdd578afd96bf'
        self.PUBLIC_KEY = 'Mp0eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a43'
        self.SIGNED_TX = 'f8900102018a4d4e540000000000000007b6f5a00eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a438a4d4e5400000000000000888ac7230489e80000808001b845f8431ba01c2c8f702d80cf64da1e9bf1f07a52e2fee8721aebe419aa9f62260a98983f89a07ed297d71d9dc37a57ffe9bb16915dccc703d8c09f30da8aadb9d5dbab8c7da9'

        self.tx = MinterDelegateTx(**{
            'nonce': 1,
            'chain_id': MinterTx.TESTNET_CHAIN_ID,
            'gas_coin': 'MNT',
            'pub_key': self.PUBLIC_KEY,
            'coin': 'MNT',
            'stake': 10
        })

    def test_valid_tx(self):
        """
        Is tx instance of MinterDelegateTx.
        """

        self.assertIsInstance(self.tx, MinterDelegateTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        signed_tx = self.tx.sign(self.PRIVATE_KEY)

        self.assertEqual(signed_tx, self.SIGNED_TX)


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
        Is tx instance of MinterDelegateTx.
        """

        self.assertIsInstance(self.TX, MinterSendCoinTx)

    def test_sign_tx(self):
        """
        Sign transaction and check signed transaction
        """
        signed_tx = self.TX.sign(self.PRIVATE_KEY)

        self.assertEqual(signed_tx, self.SIGNED_TX)

    def test_from_address(self):
        tx = MinterTx.from_raw(self.SIGNED_TX)
        self.assertEqual(tx.from_mx, self.FROM)


if __name__ == '__main__':
    unittest.main()
