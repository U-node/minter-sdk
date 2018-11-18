'''
Created on 31 окт. 2018 г.

@author: Roman
'''
import unittest
from mintersdk.sdk.transactions import MinterTx, MinterDelegateTx, MinterSendCoinTx


class TestMinterTx(unittest.TestCase):
    
    def setUp(self):
        self.SIGNED_TX = 'f88f01018a4d4e540000000000000007b6f5a00eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a438a4d4e5400000000000000880de0b6b3a7640000808001b845f8431ca078af93512fcc911a196e54fa3d9ec999b030607b7dc7f2b4cfde4f97d74ca97ea07371998b1d4dd261599aa9fd52b66c6a6f4c8ae4bd9f521905b89d5109006a06'
        self.PUBLIC_KEY = 'Mp0eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a43'
        self.TX_FROM = 'Mx9f7fd953c2c69044b901426831ed03ee0bd0597a'
        self.TX_TYPE = 7
        self.TX_STAKE = 1
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
        self.SIGNED_TX = 'f88f01018a4d4e540000000000000007b6f5a00eb98ea04ae466d8d38f490db3c99b3996a90e24243952ce9822c6dc1e2c1a438a4d4e5400000000000000880de0b6b3a7640000808001b845f8431ca078af93512fcc911a196e54fa3d9ec999b030607b7dc7f2b4cfde4f97d74ca97ea07371998b1d4dd261599aa9fd52b66c6a6f4c8ae4bd9f521905b89d5109006a06'
        self.TX_HASH = 'Mtba9219b403e4546639ee7c4a536b69bc11b97390'
        self.TX_FROM = 'Mx9f7fd953c2c69044b901426831ed03ee0bd0597a'
        
        self.tx = MinterDelegateTx(**{
                'nonce': 1,
                'gas_coin': 'MNT',
                'pub_key': self.PUBLIC_KEY,
                'coin': 'MNT',
                'stake': 1
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
        
    def test_tx_hash(self):
        """
        Validate tx hash
        """
        
        self.tx.sign(self.PRIVATE_KEY)
        self.assertEqual(self.tx.get_hash(), self.TX_HASH)
        
        
class TestMinterSendTx(unittest.TestCase):
    
    def setUp(self):
        self.PRIVATE_KEY = '07bc17abdcee8b971bb8723e36fe9d2523306d5ab2d683631693238e0f9df142'
        self.TO = 'Mx1b685a7c1e78726c48f619c497a07ed75fe00483'
        self.SIGNED_TX = 'f88301018a4d4e540000000000000001aae98a4d4e5400000000000000941b685a7c1e78726c48f619c497a07ed75fe00483880de0b6b3a7640000808001b845f8431ba05163017775fefa4d56f71ae50a8ddf361628fddc1101365b2eb6fd9b5dbdc250a02fbdc56b6cf963206f807e2899f05e4fac71f43c9adfd11ea6baa7585b8b8115'
        self.TX = MinterSendCoinTx(**{
                'nonce': 1,
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
        
        
if __name__ == '__main__':
    unittest.main()