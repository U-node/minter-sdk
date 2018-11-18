'''
Created on 28 окт. 2018 г.

@author: Roman
'''
import binascii
import rlp
import hashlib
import copy
from mintersdk import MinterConvertor, MinterHelper, MinterPrefix
from mintersdk.sdk import ECDSA
from mintersdk.sdk.wallet import MinterWallet


class MinterTx(object):
    """
    Base transaction class.
    Used only for inheritance by real transaction classes.
    """
    
    # Fee in PIP
    PAYLOAD_COMMISSION = 2
    
    # All gas price multiplied by FEE DEFAULT (PIP)
    FEE_DEFAULT_MULTIPLIER = 1000000000000000
    
    # Type of single signature for the transaction
    SIGNATURE_SINGLE_TYPE = 1
    
    # Type of multi signature for the transaction
    SIGNATURE_MULTI_TYPE = 2
    
    # Each minter transaction has:
    # Nonce - int, used for prevent transaction reply.
    # Gas Price - big int, used for managing transaction fees.
    # Gas Coin - 10 bytes, symbol of a coin to pay fee
    # Type - type of transaction (is not needed for base tx class)
    # Data - data of transaction (depends on transaction type).
    # Payload (arbitrary bytes) - arbitrary user-defined bytes.
    # Service Data - reserved field.   
    # Signature Type - single or multisig transaction.
    # Signature Data - digital signature of transaction.
    # Don't change this dict directly. You need to copy this dict and make needed changes.
    _STRUCTURE_DICT = {
            'nonce': None,
            'gas_price': None,
            'gas_coin': None,
            'type': None,
            'data': None,
            'payload': '',
            'service_data': '',
            'signature_type': None,
            'signature_data': ''
        }
    
    def __init__(self, nonce, gas_coin, payload='', service_data='', **kwargs):
        if self.__class__ is MinterTx:
            raise Exception('You can not directly create instance of MinterTx. Please use one of subclasses ({}) to create needed transaction.'.format(self.__class__.__subclasses__()))

        # Set every tx attributes
        self.nonce = nonce
        self.gas_coin = gas_coin
        self.payload = payload
        self.service_data = service_data
        
        for name, value in kwargs.items():
            setattr(self, name, value)
            
        # After all attributes are set, set gas_price in fee units.
        self._set_gas_price()        
            
    def sign(self, private_key):
        """
        Sign transaction.
        This method can be called only from instances of inherited classes.
            @param private_key|string: private key
            @return: string 
        """
        
        # Get structure populated with instance data
        tx = self._structure_from_instance()
        tx.pop('signature_data') # it's not needed before getting Keccak
        
        # Encode tx data to RLP
        tx['data'] = rlp.encode(list(tx['data'].values()))
        
        # Encode all tx to RLP and create Keccak hash
        tx_rlp = rlp.encode(list(tx.values()))
        _keccak = MinterHelper.keccak_hash(tx_rlp)
        
        # Signature data
        tx['signature_data'] = rlp.encode(
                                    ECDSA.sign(_keccak, private_key)
                                )
        
        tx_rlp = rlp.encode(list(tx.values()))
        self.signed_tx = binascii.hexlify(tx_rlp).decode()
        
        return self.signed_tx
    
    def get_hash(self):
        """
        Generate tx hash with prefix
            @return: string
        """
        if not hasattr(self, 'signed_tx') or not self.signed_tx:
            raise AttributeError('You need to sign transaction before')
        
        # Create SHA256
        sha = hashlib.sha256()
        sha.update(binascii.unhexlify(self.signed_tx))
        
        # Return first 40 symbols with prefix
        return MinterPrefix.TRANSACTION + sha.hexdigest()[:40]
            
    def _structure_from_instance(self):
        """
        Populating structure dict by instance values.
        Prepare values for signing process.
        """
        
        struct = copy.copy(self._STRUCTURE_DICT)

        struct.update({
                'nonce': self.nonce,
                'gas_price': self.gas_price,
                'gas_coin': MinterConvertor.convert_coin_name(self.gas_coin),
                'payload': self.payload,
                'service_data': self.service_data
            })
        
        return struct
    
    @classmethod    
    def _structure_to_kwargs(cls, structure):
        """
        Works with already populated structure and prepare **kwargs for
        creating new instance of tx.
        """
        
        structure.update({
                'gas_coin': structure['gas_coin'].replace(chr(0), '')
            })
        
        return structure
    
    def _set_gas_price(self):
        """
        Set gas price in BIP
        """
        
        # It is not implemented yet. We should always set gas_price to 1
#         self.gas_price = MinterConvertor.convert_value(self.get_fee(), 'bip')
        self.gas_price = 1
    
    def get_fee(self):
        """
        Get fee of transaction in PIP.
            @return: int
        """
        
        # Multiplied gas comission in PIP
        gas_price = MinterHelper.pybcmul(self.COMMISSION, self.FEE_DEFAULT_MULTIPLIER)
        
        # Comission for payload and service_data bytes
        comission = MinterHelper.pybcadd(
                        MinterHelper.pybcmul(len(self.payload), self.FEE_DEFAULT_MULTIPLIER),
                        MinterHelper.pybcmul(len(self.service_data), self.FEE_DEFAULT_MULTIPLIER)
                    )
        
        return int(MinterHelper.pybcadd(gas_price, comission))
        
    @classmethod
    def from_raw(cls, raw_tx):
        """
        Generate tx object from raw tx
            @param raw_tx: string
            @return: MinterTx child instance
        """
        
        tx = rlp.decode(binascii.unhexlify(raw_tx))
        
        # Populate structure dict with decoded tx data
        struct = copy.copy(cls._STRUCTURE_DICT)
        struct.update({
                'nonce': int(binascii.hexlify(tx[0]), 16),
                'gas_price': int(binascii.hexlify(tx[1]), 16),
                'gas_coin': tx[2].decode(),
                'type': int(binascii.hexlify(tx[3]), 16),
                'payload': tx[5].decode().replace(chr(0), ''),
                'service_data': tx[6].decode().replace(chr(0), ''),
                'signature_type': int(binascii.hexlify(tx[7]), 16)
            })
        
        # Get signature data
        signature_data =  rlp.decode(tx[8])
        struct.update({
                'signature_data': {
                        'v': int(binascii.hexlify(signature_data[0]), 16),
                        'r': binascii.hexlify(signature_data[1]).decode(),
                        's': binascii.hexlify(signature_data[2]).decode()
                    }
            })        
        
        # Find out which of tx instance need to create depending on its type
        data = rlp.decode(tx[4])
        if struct['type'] == MinterDelegateTx.TYPE:
            _class = MinterDelegateTx
        elif struct['type'] == MinterSendCoinTx.TYPE:
            _class = MinterSendCoinTx
        else:
            raise Exception('Undefined tx type.')
            
        # Set tx data to minter dict
        struct.update({
                'data': _class._data_from_raw(data)
            })
            
        # Recover public key.
        # We should not change curent struct, so pass copy of the struct to recover method.
        public_key = cls.recover_public_key(copy.copy(struct))
        struct.update({
                'from_mx': MinterWallet.get_address_from_public_key(public_key),
                'signed_tx': raw_tx
            })
        
        
        # Prepare **kwargs for creating _class instance.
        # Pass copy of the struct.
        kwargs = _class._structure_to_kwargs(copy.copy(struct))
        
        return _class(**kwargs)
    
    @classmethod
    def recover_public_key(cls, tx):
        """
        Recover public key from tx.
            @return: string
        """
        
        # Remember signature data and remove it from tx
        signature_data = tx.pop('signature_data')

        # Unxelify (convert to bin (ascii)) all non numeric dict values
        tx = MinterHelper.hex2bin_recursive(tx)
        
        # Encode tx data to RLP
        tx['data'] = rlp.encode(list(tx['data'].values()))
        
        # Message
        tx_rlp = rlp.encode(list(tx.values()))
        _keccak = MinterHelper.keccak_hash(tx_rlp)
        
        # Recover public key
        public_key = ECDSA.recover(_keccak, tuple(signature_data.values()))
        
        return MinterPrefix.PUBLIC_KEY + public_key        
                
    @classmethod
    def _data_from_raw(cls, raw_data):
        """
        Decoding tx data to tx attributes.
        Docoding depends on tx type, so this method must be implemented in each child class.
        """
        raise NotImplementedError
        
    
class MinterBuyCoinTx(MinterTx):
    """
    Buy coin transaction
    """
    
    # Type of transaction
    TYPE = 4
    
    # Fee units
    COMMISSION = 100
    
    
class MinterCreateCoinTx(MinterTx):
    """
    Create coin transaction
    """
    
    # Type of transaction
    TYPE = 5
    
    # Fee units
    COMMISSION = 1000
    
    
class MinterDeclareCandidacyTx(MinterTx):
    """
    Declare candidacy transaction
    """
    
    # Type of transaction
    TYPE = 6
    
    # Fee units
    COMMISSION = 10000
    
    
class MinterDelegateTx(MinterTx):
    """
    Delegate transaction
    """
    
    # Type of transaction
    TYPE = 7
    
    # Fee units
    COMMISSION = 100
    
    def __init__(self, pub_key, coin, stake, **kwargs):
        super().__init__(**kwargs)
        
        self.pub_key = pub_key
        self.coin = coin
        self.stake = stake
        
    def _structure_from_instance(self):
        """
        Override parent method to add tx special data.
        """
        
        struct = super()._structure_from_instance()

        struct.update({
                'type': self.TYPE,
                'data': {
                        'pub_key': binascii.unhexlify(MinterPrefix.remove_prefix(self.pub_key, MinterPrefix.PUBLIC_KEY)),
                        'coin': MinterConvertor.convert_coin_name(self.coin),
                        'stake': MinterConvertor.convert_value(self.stake, 'pip')
                    },
                'signature_type': self.SIGNATURE_SINGLE_TYPE
            })
        
        return struct
    
    @classmethod
    def _structure_to_kwargs(cls, structure):
        """
        Prepare decoded structure data to instance kwargs.
        """
        
        kwargs = super()._structure_to_kwargs(structure)
        
        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
                'pub_key': MinterPrefix.PUBLIC_KEY + binascii.hexlify(kwargs['data']['pub_key']).decode(),
                'coin': kwargs['data']['coin'].decode().replace(chr(0), ''),
                'stake': MinterConvertor.convert_value(
                                    int(binascii.hexlify(kwargs['data']['stake']), 16),
                                    'bip'
                                )
            })
        
        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])
        
        return kwargs
    
    @classmethod
    def _data_from_raw(cls, raw_data):
        """
        Parent method implementation
        """
        return {
                'pub_key': binascii.hexlify(raw_data[0]).decode(),
                'coin': binascii.hexlify(raw_data[1]).decode(),
                'stake': binascii.hexlify(raw_data[2]).decode()
            }
    
    
class MinterRedeemCheckTx(MinterTx):
    """
    Redeem check transaction
    """
    
    # Type of transaction
    TYPE = 9
    
    # Fee units
    COMMISSION = 10
    
    
class MinterSellAllCoinTx(MinterTx):
    """
    Sell all coin transaction
    """
    
    # Type of transaction
    TYPE = 3
    
    # Fee units
    COMMISSION = 100
    
    
class MinterSellCoinTx(MinterTx):
    """
    Sell coin transaction
    """
    
    # Type of transaction
    TYPE = 2
    
    # Fee units
    COMMISSION = 100
    
    
class MinterSendCoinTx(MinterTx):
    """
    Send coin transaction
    """
    
    # Type of transaction
    TYPE = 1
    
    # Fee units
    COMMISSION = 10
    
    def __init__(self, coin, to, value, **kwargs):
        super().__init__(**kwargs)
        
        self.coin = coin
        self.to = to
        self.value = value
        
    def _structure_from_instance(self):
        """
        Override parent method to add tx special data.
        """
        
        struct = super()._structure_from_instance()

        struct.update({
                'type': self.TYPE,
                'data': {
                        'coin': MinterConvertor.convert_coin_name(self.coin),
                        'to': binascii.unhexlify(MinterPrefix.remove_prefix(self.to, MinterPrefix.ADDRESS)),
                        'value': MinterConvertor.convert_value(self.value, 'pip')
                    },
                'signature_type': self.SIGNATURE_SINGLE_TYPE
            })
        
        return struct
    
    @classmethod
    def _structure_to_kwargs(cls, structure):
        """
        Prepare decoded structure data to instance kwargs.
        """
        
        kwargs = super()._structure_to_kwargs(structure)
        
        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
                'coin': kwargs['data']['coin'].decode().replace(chr(0), ''),
                'to': MinterPrefix.ADDRESS + binascii.hexlify(kwargs['data']['to']).decode(),
                'value': MinterConvertor.convert_value(
                                    int(binascii.hexlify(kwargs['data']['value']), 16),
                                    'bip'
                                )
            })
        
        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])
        
        return kwargs
    
    @classmethod
    def _data_from_raw(cls, raw_data):
        """
        Parent method implementation
        """
        return {
                'coin': binascii.hexlify(raw_data[0]).decode(),
                'to': binascii.hexlify(raw_data[1]).decode(),
                'value': binascii.hexlify(raw_data[2]).decode()
            }
    
    
class MinterSetCandidateOffTx(MinterTx):
    """
    Set candidate OFF transaction
    """
    
    # Type of transaction
    TYPE = 11
    
    # Fee units
    COMMISSION = 100
    
    
class MinterSetCandidateOnTx(MinterTx):
    """
    Set candidate ON transaction
    """
    
    # Type of transaction
    TYPE = 10
    
    # Fee units
    COMMISSION = 100
    
    
class MinterUnbondTx(MinterTx):
    """
    Unbound transaction
    """
    
    # Type of transaction
    TYPE = 8
    
    # Fee units
    COMMISSION = 100