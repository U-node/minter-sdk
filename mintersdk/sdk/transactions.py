"""
@author: Roman Matusevich
"""
import rlp
import hashlib
import copy
from mintersdk import (
    MinterHelper, PREFIX_ADDR, PREFIX_TX, PREFIX_PUBKEY, PREFIX_CHECK
)
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

    # Main net chain id
    MAINNET_CHAIN_ID = 1

    # Test net chain id
    TESTNET_CHAIN_ID = 2

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
    # Don't change this dict directly. You need to copy this dict
    # and make needed changes.
    _STRUCTURE_DICT = {
        'nonce': None,
        'chain_id': None,
        'gas_price': None,
        'gas_coin': None,
        'type': None,
        'data': None,
        'payload': '',
        'service_data': '',
        'signature_type': None,
        'signature_data': ''
    }

    def __init__(self, nonce, gas_coin, payload='', service_data='',
                 chain_id=1, gas_price=1, **kwargs):
        if self.__class__ is MinterTx:
            exc_msg = """You can not directly create instance of MinterTx.
            Please use one of subclasses ({}) to create needed transaction."""
            raise Exception(exc_msg.format(self.__class__.__subclasses__()))

        # Set every tx attributes
        self.nonce = nonce
        self.chain_id = chain_id
        self.gas_coin = gas_coin.upper()
        self.gas_price = gas_price
        self.payload = payload
        self.service_data = service_data
        self.signature_type = None
        self.signed_tx = None

        for name, value in kwargs.items():
            setattr(self, name, value)

    def generate_tx_rlp(self):
        """
        Create structure from instance and prepare rlp structure
        Returns:
            tx_struct (dict)
        """
        # Get structure populated with instance data
        tx_struct = self._structure_from_instance()
        # Remove signature data, it's not needed before getting Keccak
        tx_struct.pop('signature_data')

        # Encode tx data to RLP
        tx_struct['data'] = rlp.encode(list(tx_struct['data'].values()))

        return tx_struct

    @staticmethod
    def generate_signed_tx(tx_struct):
        """
        Generate signed tx hash from it's structure
        Args:
            tx_struct (dict): populated tx structure dict
        Returns:
            signed_tx hash (str)
        """
        tx_rlp = rlp.encode(list(tx_struct.values()))
        return tx_rlp.hex()

    def generate_signature(self, private_key):
        """
        Create signature for transaction
        Args:
            private_key (str): private key to sign with
        Returns:
            hex_signature (str)
        """
        # Get structure populated with instance data and rlp encoded
        tx_struct = self.generate_tx_rlp()

        # Create keccak hash
        tx_rlp = rlp.encode(list(tx_struct.values()))
        keccak = MinterHelper.keccak_hash(tx_rlp)

        # Create signature
        signature = ECDSA.sign(keccak, private_key)
        signature = rlp.encode(signature).hex()

        return signature

    def sign(self, private_key=None, signature=None, ms_address=None):
        """
        Sign transaction.
        This method can be called only from instances of inherited
        classes.
        Args:
            private_key (string|list[string]): private key to sign with
            signature (string|list[string]): signature to sign with
            ms_address (string): Multi signature address to sign tx by
        """
        # Check arguments validity
        if not private_key and not signature:
            raise Exception(
                'Please, provide either `private_key(s)` or `signature(s)`'
            )
        if not ms_address and private_key and type(private_key) is not str:
            raise Exception(
                '''
                Please, provide a single `private_key` or set `ms_address` 
                argument for multisig tx
                '''
            )
        if not ms_address and signature and type(signature) is not str:
            raise Exception(
                '''
                Please, provide a single `signature` or set `ms_address` 
                argument for multisig tx
                '''
            )

        # Set tx signature type
        self.signature_type = self.SIGNATURE_SINGLE_TYPE
        if ms_address:
            if type(private_key) is str:
                private_key = [private_key]
            if type(signature) is str:
                signature = [signature]
            self.signature_type = self.SIGNATURE_MULTI_TYPE

        # Get populated and rlp encoded tx structure
        tx_struct = self.generate_tx_rlp()

        # Signature data
        if self.signature_type == self.SIGNATURE_SINGLE_TYPE:
            # Only one of private_key or signature can be provided for
            # single signature type tx
            if private_key and signature:
                raise Exception(
                    '''
                    Please, provide one of `private_key` or `signature` for 
                    single signature type tx
                    '''
                )

            # Set signature_data
            if private_key:
                signature_data = self.generate_signature(private_key)
            else:
                signature_data = signature
            signature_data = self.decode_signature(signature_data)
        else:
            # Add multisig address to signature
            signature_data = [
                bytes.fromhex(MinterHelper.prefix_remove(ms_address)),
                []
            ]

            # Sign by each private key and add to total signature data
            if private_key:
                for pk in private_key:
                    _signature = self.generate_signature(pk)
                    signature_data[1].append(self.decode_signature(_signature))

            # Sign by each signature and add to total signature data
            if signature:
                for _signature in signature:
                    signature_data[1].append(self.decode_signature(_signature))
        tx_struct['signature_data'] = rlp.encode(signature_data)

        self.signed_tx = self.generate_signed_tx(tx_struct)

    def get_hash(self):
        """
        Generate tx hash with prefix
        Returns:
            string
        """
        if not hasattr(self, 'signed_tx') or not self.signed_tx:
            raise AttributeError('You need to sign transaction before')

        # Create SHA256
        sha = hashlib.sha256()
        sha.update(bytes.fromhex(self.signed_tx))

        # Return first 40 symbols with prefix
        return MinterHelper.prefix_add(sha.hexdigest()[:40], PREFIX_TX)

    def _structure_from_instance(self):
        """
        Populating structure dict by instance values.
        Prepare values for signing process.
        """

        struct = copy.copy(self._STRUCTURE_DICT)

        struct.update({
            'nonce': self.nonce,
            'chain_id': self.chain_id,
            'gas_price': self.gas_price,
            'gas_coin': MinterHelper.encode_coin_name(self.gas_coin),
            'payload': self.payload,
            'service_data': self.service_data,
            'signature_type': self.signature_type
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """
        Works with already populated structure and prepare **kwargs for
        creating new instance of tx.
        """

        structure.update({
            'gas_coin': MinterHelper.decode_coin_name(structure['gas_coin'])
        })

        return structure

    def get_fee(self):
        """
        Get fee of transaction in PIP.
        Returns:
            int
        """
        # Commission for payload and service_data bytes
        payload_gas = (
            MinterHelper.bytes_len(self.payload) * self.PAYLOAD_COMMISSION
        )
        service_data_gas = (
            MinterHelper.bytes_len(self.service_data) * self.PAYLOAD_COMMISSION
        )

        # Total commission
        commission = self.COMMISSION + payload_gas + service_data_gas
        commission *= self.FEE_DEFAULT_MULTIPLIER

        return commission

    @classmethod
    def from_raw(cls, raw_tx):
        """
        Generate tx object from raw tx
        Args:
            raw_tx (string)
        Returns:
            MinterTx child instance
        """

        tx = rlp.decode(bytes.fromhex(raw_tx))

        # Try to decode payload
        try:
            payload = tx[6].decode()
        except UnicodeDecodeError:
            payload = tx[6]

        # Try to decode service data
        try:
            service_data = tx[7].decode()
        except UnicodeDecodeError:
            service_data = tx[7]

        # Populate structure dict with decoded tx data
        struct = copy.copy(cls._STRUCTURE_DICT)
        struct.update({
            'nonce': int.from_bytes(tx[0], 'big'),
            'chain_id': int.from_bytes(tx[1], 'big'),
            'gas_price': int.from_bytes(tx[2], 'big'),
            'gas_coin': tx[3].decode(),
            'type': int.from_bytes(tx[4], 'big'),
            'payload': payload,
            'service_data': service_data,
            'signature_type': int.from_bytes(tx[8], 'big')
        })

        # Get signature data
        signature_data = rlp.decode(tx[9])
        if struct['signature_type'] == cls.SIGNATURE_SINGLE_TYPE:
            signature_data = {
                'v': int.from_bytes(signature_data[0], 'big'),
                'r': signature_data[1].hex(),
                's': signature_data[2].hex()
            }
        else:
            # Decode signatures
            signatures = []
            for signature in signature_data[1]:
                signatures.append({
                    'v': int.from_bytes(signature[0], 'big'),
                    'r': signature[1].hex(),
                    's': signature[2].hex()
                })

            # Create decoded signature data
            signature_data = {
                'from_mx': MinterHelper.prefix_add(
                    signature_data[0].hex(), PREFIX_ADDR
                ),
                'signatures': signatures
            }
        struct['signature_data'] = signature_data

        # Find out which of tx instance need to create depending on it's type
        data = rlp.decode(tx[5])
        if struct['type'] == MinterDelegateTx.TYPE:
            _class = MinterDelegateTx
        elif struct['type'] == MinterSendCoinTx.TYPE:
            _class = MinterSendCoinTx
        elif struct['type'] == MinterBuyCoinTx.TYPE:
            _class = MinterBuyCoinTx
        elif struct['type'] == MinterCreateCoinTx.TYPE:
            _class = MinterCreateCoinTx
        elif struct['type'] == MinterDeclareCandidacyTx.TYPE:
            _class = MinterDeclareCandidacyTx
        elif struct['type'] == MinterRedeemCheckTx.TYPE:
            _class = MinterRedeemCheckTx
        elif struct['type'] == MinterSellAllCoinTx.TYPE:
            _class = MinterSellAllCoinTx
        elif struct['type'] == MinterSellCoinTx.TYPE:
            _class = MinterSellCoinTx
        elif struct['type'] == MinterSetCandidateOffTx.TYPE:
            _class = MinterSetCandidateOffTx
        elif struct['type'] == MinterSetCandidateOnTx.TYPE:
            _class = MinterSetCandidateOnTx
        elif struct['type'] == MinterUnbondTx.TYPE:
            _class = MinterUnbondTx
        elif struct['type'] == MinterEditCandidateTx.TYPE:
            _class = MinterEditCandidateTx
        elif struct['type'] == MinterMultiSendCoinTx.TYPE:
            _class = MinterMultiSendCoinTx
        else:
            raise Exception('Undefined tx type.')

        # Set tx data
        struct['data'] = _class._data_from_raw(data)

        # Set sender address and raw tx to minter dict
        # ONLY AFTER tx data was set
        struct.update({
            'from_mx': cls.get_sender_address(tx=copy.copy(struct)),
            'signed_tx': raw_tx
        })

        # Prepare **kwargs for creating _class instance.
        # Pass copy of the struct.
        kwargs = _class._structure_to_kwargs(copy.copy(struct))

        return _class(**kwargs)

    @classmethod
    def get_sender_address(cls, tx):
        """
        Get sender address from tx.
        Recover public key from tx and then get address from public key,
        if tx has single signature type, or get decoded sender address,
        if tx has multi signature type.
        Args:
            tx (dict): transaction dict
        Returns:
            Minter address (string)
        """

        # Remember signature data and remove it from tx
        signature_data = tx.pop('signature_data')

        # If there is sender address in signature data (multi signature tx),
        # return it
        if signature_data.get('from_mx'):
            return signature_data['from_mx']

        # Otherwise (single signature tx), recover public key and get
        # address from public key
        # Unhexlify hexdigit dict values to bytes
        tx = MinterHelper.hex2bin_recursive(tx)

        # Encode tx data to RLP
        tx['data'] = rlp.encode(list(tx['data'].values()))

        # Message
        tx_rlp = rlp.encode(list(tx.values()))
        _keccak = MinterHelper.keccak_hash(tx_rlp)

        # Recover public key
        public_key = MinterHelper.prefix_add(
            ECDSA.recover(_keccak, tuple(signature_data.values())),
            PREFIX_PUBKEY
        )

        return MinterWallet.get_address_from_public_key(public_key)

    @classmethod
    def add_signature(cls, signed_tx, private_key):
        """
        Add signature to already signed tx. Method is available only for multisig txs
        Args:
            signed_tx (str): signed tx
            private_key (str): private key
        Returns:
            tx object
        """

        # Create tx instance from raw tx
        tx = cls.from_raw(signed_tx)

        # Check tx to be multi signature type
        if tx.signature_type != cls.SIGNATURE_MULTI_TYPE:
            raise Exception(
                'Signature can be added only to tx with multi signature type'
            )

        # Convert signature data from verbose dict to needed list of
        # signatures
        signature_data = [
            bytes.fromhex(
                MinterHelper.prefix_remove(tx.signature_data['from_mx'])
            ),
            []
        ]
        for item in tx.signature_data['signatures']:
            # Create raw signature (values as integers)
            raw = [
                item['v'],
                int(item['r'], 16),
                int(item['s'], 16)
            ]
            # Append raw signature to total signature data
            signature_data[1].append(raw)

        # Get tx populated structure and keccak hash from this structure
        tx_struct = tx.generate_tx_rlp()

        # Create new signature and update signatures list and signatures
        # attribute of tx
        signature = cls.decode_signature(
            signature=tx.generate_signature(private_key)
        )
        signature_data[1].append(signature)
        tx.signature_data['signatures'].append({
            'v': signature[0],
            'r': format(signature[1], 'x'),
            's': format(signature[2], 'x')
        })

        # Update resulting struct signature data
        tx_struct['signature_data'] = rlp.encode(signature_data)

        # Generate new signed tx and update tx object attribute
        tx.signed_tx = cls.generate_signed_tx(tx_struct)

        return tx

    @classmethod
    def decode_signature(cls, signature):
        """
        Decode hexed signature to raw signature (list of integers)
        Args:
            signature (str): hexed signature
        Returns:
            signature (list[int])
        """
        signature = bytes.fromhex(signature)
        signature = rlp.decode(signature)
        signature = [int.from_bytes(item, 'big') for item in signature]

        return signature

    @classmethod
    def _data_from_raw(cls, raw_data):
        """
        Decoding tx data to tx attributes.
        Decoding depends on tx type, so this method
        must be implemented in each child class.
        """
        raise NotImplementedError


class MinterBuyCoinTx(MinterTx):
    """ Buy coin transaction """

    # Type of transaction
    TYPE = 4

    # Fee units
    COMMISSION = 100

    def __init__(self, coin_to_buy, value_to_buy, coin_to_sell,
                 max_value_to_sell, **kwargs):
        """
        Args:
            coin_to_buy (str): coin name to buy
            value_to_buy (float|int): how much coin to buy (BIP)
            coin_to_sell (str): coin name to sell
            max_value_to_sell (float|int): max amount to sell (BIP)
        """

        super().__init__(**kwargs)

        self.coin_to_buy = coin_to_buy.upper()
        self.value_to_buy = value_to_buy
        self.coin_to_sell = coin_to_sell.upper()
        self.max_value_to_sell = max_value_to_sell

    def _structure_from_instance(self):
        """ Override parent method. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'coin_to_buy': MinterHelper.encode_coin_name(self.coin_to_buy),
                'value_to_buy': MinterHelper.to_pip(self.value_to_buy),
                'coin_to_sell': MinterHelper.encode_coin_name(self.coin_to_sell),
                'max_value_to_sell': MinterHelper.to_pip(self.max_value_to_sell)
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'coin_to_buy': MinterHelper.decode_coin_name(
                kwargs['data']['coin_to_buy']
            ),
            'value_to_buy': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['value_to_buy'], 'big')
            ),
            'coin_to_sell': MinterHelper.decode_coin_name(
                kwargs['data']['coin_to_sell']
            ),
            'max_value_to_sell': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['max_value_to_sell'], 'big')
            )
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'coin_to_buy': raw_data[0],
            'value_to_buy': raw_data[1],
            'coin_to_sell': raw_data[2],
            'max_value_to_sell': raw_data[3]
        }


class MinterCreateCoinTx(MinterTx):
    """ Create coin transaction """

    # Type of transaction
    TYPE = 5

    # Fee units
    COMMISSION = 1000

    def __init__(self, name, symbol, initial_amount, initial_reserve, crr,
                 max_supply, **kwargs):
        """
        Args:
            name (str): coin name
            symbol (str): coin symbol
            initial_amount (float|int): amount in BIP
            initial_reserve (float|int): reserve in BIP
            crr (int)
        """

        super().__init__(**kwargs)

        self.name = name
        self.symbol = symbol.upper()
        self.initial_amount = initial_amount
        self.initial_reserve = initial_reserve
        self.crr = crr
        self.max_supply = max_supply

    def _structure_from_instance(self):
        """ Override parent method. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'name': self.name,
                'symbol': MinterHelper.encode_coin_name(self.symbol),
                'initial_amount': MinterHelper.to_pip(self.initial_amount),
                'initial_reserve': MinterHelper.to_pip(self.initial_reserve),
                'crr': '' if self.crr == 0 else self.crr,
                'max_supply': MinterHelper.to_pip(self.max_supply)
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'name': kwargs['data']['name'].decode(),
            'symbol': MinterHelper.decode_coin_name(kwargs['data']['symbol']),
            'initial_amount': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['initial_amount'], 'big')
            ),
            'initial_reserve': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['initial_reserve'], 'big')
            ),
            'crr': int.from_bytes(kwargs['data']['crr'], 'big'),
            'max_supply': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['max_supply'], 'big')
            )
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'name': raw_data[0],
            'symbol': raw_data[1],
            'initial_amount': raw_data[2],
            'initial_reserve': raw_data[3],
            'crr': raw_data[4],
            'max_supply': raw_data[5]
        }


class MinterDeclareCandidacyTx(MinterTx):
    """ Declare candidacy transaction """

    # Type of transaction
    TYPE = 6

    # Fee units
    COMMISSION = 10000

    def __init__(self, address, pub_key, commission, coin, stake, **kwargs):
        """
        Args:
            address (str): candidate address
            pub_key (str): candidate public key
            commission (int): candidate commission
            coin (str): coin name
            stake (float|int): stake in BIP
        """

        super().__init__(**kwargs)

        self.address = address
        self.pub_key = pub_key
        self.commission = '' if commission == 0 else commission
        self.coin = coin.upper()
        self.stake = stake

    def _structure_from_instance(self):
        """ Override parent method. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'address': bytes.fromhex(
                    MinterHelper.prefix_remove(self.address)
                ),
                'pub_key': bytes.fromhex(
                    MinterHelper.prefix_remove(self.pub_key)
                ),
                'commission': '' if self.commission == 0 else self.commission,
                'coin': MinterHelper.encode_coin_name(self.coin),
                'stake': MinterHelper.to_pip(self.stake)
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'address': MinterHelper.prefix_add(
                kwargs['data']['address'].hex(), PREFIX_ADDR
            ),
            'pub_key': MinterHelper.prefix_add(
                kwargs['data']['pub_key'].hex(), PREFIX_PUBKEY
            ),
            'commission': int.from_bytes(kwargs['data']['commission'], 'big'),
            'coin': MinterHelper.decode_coin_name(kwargs['data']['coin']),
            'stake': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['stake'], 'big')
            )
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'address': raw_data[0],
            'pub_key': raw_data[1],
            'commission': raw_data[2],
            'coin': raw_data[3],
            'stake': raw_data[4]
        }


class MinterDelegateTx(MinterTx):
    """ Delegate transaction """

    # Type of transaction
    TYPE = 7

    # Fee units
    COMMISSION = 200

    def __init__(self, pub_key, coin, stake, **kwargs):
        super().__init__(**kwargs)

        self.pub_key = pub_key
        self.coin = coin.upper()
        self.stake = stake

    def _structure_from_instance(self):
        """ Override parent method to add tx special data. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'pub_key': bytes.fromhex(
                    MinterHelper.prefix_remove(self.pub_key)
                ),
                'coin': MinterHelper.encode_coin_name(self.coin),
                'stake': MinterHelper.to_pip(self.stake)
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """
        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'pub_key': MinterHelper.prefix_add(
                kwargs['data']['pub_key'].hex(), PREFIX_PUBKEY
            ),
            'coin': MinterHelper.decode_coin_name(kwargs['data']['coin']),
            'stake': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['stake'], 'big')
            )
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'pub_key': raw_data[0],
            'coin': raw_data[1],
            'stake': raw_data[2]
        }


class MinterRedeemCheckTx(MinterTx):
    """ Redeem check transaction """

    # Type of transaction
    TYPE = 9

    # Fee units
    COMMISSION = 10

    def __init__(self, check, proof, **kwargs):
        """
        Args:
            check (str)
            proof (str)
        """

        super().__init__(**kwargs)

        self.check = check
        self.proof = proof

    def _structure_from_instance(self):
        """ Override parent method to add tx special data. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'check': bytes.fromhex(MinterHelper.prefix_remove(self.check)),
                'proof': bytes.fromhex(self.proof)
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'check': MinterHelper.prefix_add(
                kwargs['data']['check'].hex(), PREFIX_CHECK
            ),
            'proof': kwargs['data']['proof'].hex()
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'check': raw_data[0],
            'proof': raw_data[1]
        }


class MinterSellAllCoinTx(MinterTx):
    """ Sell all coin transaction """

    # Type of transaction
    TYPE = 3

    # Fee units
    COMMISSION = 100

    def __init__(self, coin_to_sell, coin_to_buy, min_value_to_buy, **kwargs):
        """
        Args:
            coin_to_sell (str)
            coin_to_buy (str)
            min_value_to_buy (float|int): BIP
        """

        super().__init__(**kwargs)

        self.coin_to_sell = coin_to_sell.upper()
        self.coin_to_buy = coin_to_buy.upper()
        self.min_value_to_buy = min_value_to_buy

    def _structure_from_instance(self):
        """ Override parent method to add tx special data. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'coin_to_sell': MinterHelper.encode_coin_name(self.coin_to_sell),
                'coin_to_buy': MinterHelper.encode_coin_name(self.coin_to_buy),
                'min_value_to_buy': MinterHelper.to_pip(self.min_value_to_buy)
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'coin_to_sell': MinterHelper.decode_coin_name(
                kwargs['data']['coin_to_sell']
            ),
            'coin_to_buy': MinterHelper.decode_coin_name(
                kwargs['data']['coin_to_buy']
            ),
            'min_value_to_buy': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['min_value_to_buy'], 'big')
            )
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'coin_to_sell': raw_data[0],
            'coin_to_buy': raw_data[1],
            'min_value_to_buy': raw_data[2]
        }


class MinterSellCoinTx(MinterTx):
    """ Sell coin transaction """

    # Type of transaction
    TYPE = 2

    # Fee units
    COMMISSION = 100

    def __init__(self, coin_to_sell, value_to_sell, coin_to_buy,
                 min_value_to_buy, **kwargs):
        """
        Args:
            coin_to_sell (str)
            value_to_sell (float|int): BIP
            coin_to_buy (str)
            min_value_to_buy (float|int): BIP
        """

        super().__init__(**kwargs)

        self.coin_to_sell = coin_to_sell.upper()
        self.value_to_sell = value_to_sell
        self.coin_to_buy = coin_to_buy.upper()
        self.min_value_to_buy = min_value_to_buy

    def _structure_from_instance(self):
        """ Override parent method to add tx special data. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'coin_to_sell': MinterHelper.encode_coin_name(self.coin_to_sell),
                'value_to_sell': MinterHelper.to_pip(self.value_to_sell),
                'coin_to_buy': MinterHelper.encode_coin_name(self.coin_to_buy),
                'min_value_to_buy': MinterHelper.to_pip(self.min_value_to_buy)
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'coin_to_sell': MinterHelper.decode_coin_name(
                kwargs['data']['coin_to_sell']
            ),
            'value_to_sell': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['value_to_sell'], 'big')
            ),
            'coin_to_buy': MinterHelper.decode_coin_name(
                kwargs['data']['coin_to_buy']
            ),
            'min_value_to_buy': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['min_value_to_buy'], 'big')
            )
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'coin_to_sell': raw_data[0],
            'value_to_sell': raw_data[1],
            'coin_to_buy': raw_data[2],
            'min_value_to_buy': raw_data[3]
        }


class MinterSendCoinTx(MinterTx):
    """ Send coin transaction """

    # Type of transaction
    TYPE = 1

    # Fee units
    COMMISSION = 10

    def __init__(self, coin, to, value, **kwargs):
        super().__init__(**kwargs)

        self.coin = coin.upper()
        self.to = to
        self.value = value

    def _structure_from_instance(self):
        """ Override parent method to add tx special data. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'coin': MinterHelper.encode_coin_name(self.coin),
                'to': bytes.fromhex(MinterHelper.prefix_remove(self.to)),
                'value': MinterHelper.to_pip(self.value)
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'coin': MinterHelper.decode_coin_name(kwargs['data']['coin']),
            'to': MinterHelper.prefix_add(
                kwargs['data']['to'].hex(), PREFIX_ADDR
            ),
            'value': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['value'], 'big')
            )
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'coin': raw_data[0],
            'to': raw_data[1],
            'value': raw_data[2]
        }


class MinterMultiSendCoinTx(MinterTx):
    """ Multi send transaction """

    # Type of transaction
    TYPE = 13

    # Fee units
    COMMISSION = 10
    COMMISSION_PER_RECIPIENT = 5

    def __init__(self, txs, **kwargs):
        """
        Args:
            txs (list[dict{coin, to, value}]): list of send coin data
        """
        super().__init__(**kwargs)

        self.txs = txs

    def get_fee(self):
        """
        Override parent method to calc
        multisend-specific fee: (n_txs - 1) * 5 units
        """
        base_fee = super().get_fee()
        recipients_fee = (
            (len(self.txs)-1) * self.COMMISSION_PER_RECIPIENT *
            self.FEE_DEFAULT_MULTIPLIER
        )

        return base_fee + recipients_fee

    def _structure_from_instance(self):
        """ Override parent method to add tx special data. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'txs': []
            }
        })

        # Populate multi data from each single tx.
        for item in self.txs:
            struct['data']['txs'].append([
                MinterHelper.encode_coin_name(item['coin'].upper()),
                bytes.fromhex(MinterHelper.prefix_remove(item['to'])),
                MinterHelper.to_pip(item['value'])
            ])

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        for index, item in enumerate(kwargs['data']['txs']):
            kwargs['data']['txs'][index] = {
                'coin': MinterHelper.decode_coin_name(item[0]),
                'to': MinterHelper.prefix_add(item[1].hex(), PREFIX_ADDR),
                'value': MinterHelper.to_pip(int.from_bytes(item[2], 'big'))
            }

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        data = {'txs': []}
        for item in raw_data[0]:
            data['txs'].append([item[0], item[1], item[2]])

        return data


class MinterSetCandidateOffTx(MinterTx):
    """ Set candidate OFF transaction """

    # Type of transaction
    TYPE = 11

    # Fee units
    COMMISSION = 100

    def __init__(self, pub_key, **kwargs):
        """
        Args:
            pub_key (str)
        """

        super().__init__(**kwargs)

        self.pub_key = pub_key

    def _structure_from_instance(self):
        """ Override parent method to add tx special data. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'pub_key': bytes.fromhex(
                    MinterHelper.prefix_remove(self.pub_key)
                )
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'pub_key': MinterHelper.prefix_add(
                kwargs['data']['pub_key'].hex(), PREFIX_PUBKEY
            )
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'pub_key': raw_data[0]
        }


class MinterSetCandidateOnTx(MinterTx):
    """ Set candidate ON transaction """

    # Type of transaction
    TYPE = 10

    # Fee units
    COMMISSION = 100

    def __init__(self, pub_key, **kwargs):
        """
        Args:
            pub_key (str)
        """

        super().__init__(**kwargs)

        self.pub_key = pub_key

    def _structure_from_instance(self):
        """ Override parent method to add tx special data. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'pub_key': bytes.fromhex(
                    MinterHelper.prefix_remove(self.pub_key)
                )
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'pub_key': MinterHelper.prefix_add(
                kwargs['data']['pub_key'].hex(), PREFIX_PUBKEY
            )
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'pub_key': raw_data[0]
        }


class MinterUnbondTx(MinterTx):
    """ Unbond transaction """

    # Type of transaction
    TYPE = 8

    # Fee units
    COMMISSION = 100

    def __init__(self, pub_key, coin, value, **kwargs):
        """
        Args:
            pub_key (str)
            coin (str)
            value (float|int): BIP
        """

        super().__init__(**kwargs)

        self.pub_key = pub_key
        self.coin = coin.upper()
        self.value = value

    def _structure_from_instance(self):
        """ Override parent method to add tx special data. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'pub_key': bytes.fromhex(
                    MinterHelper.prefix_remove(self.pub_key)
                ),
                'coin': MinterHelper.encode_coin_name(self.coin),
                'value': MinterHelper.to_pip(self.value)
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'pub_key': MinterHelper.prefix_add(
                kwargs['data']['pub_key'].hex(), PREFIX_PUBKEY
            ),
            'coin': MinterHelper.decode_coin_name(kwargs['data']['coin']),
            'value': MinterHelper.to_bip(
                int.from_bytes(kwargs['data']['value'], 'big')
            )
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'pub_key': raw_data[0],
            'coin': raw_data[1],
            'value': raw_data[2]
        }


class MinterEditCandidateTx(MinterTx):
    """ Edit candidate transaction """

    # Type of transaction
    TYPE = 14

    # Fee units
    COMMISSION = 10000

    def __init__(self, pub_key, reward_address, owner_address, **kwargs):
        """
        Args:
            pub_key (str): candidate public key
            reward_address (str)
            owner_address (str)
        """

        super().__init__(**kwargs)

        self.pub_key = pub_key
        self.reward_address = reward_address
        self.owner_address = owner_address

    def _structure_from_instance(self):
        """ Override parent method to add tx special data. """

        struct = super()._structure_from_instance()

        struct.update({
            'type': self.TYPE,
            'data': {
                'pub_key': bytes.fromhex(
                    MinterHelper.prefix_remove(self.pub_key)
                ),
                'reward_address': bytes.fromhex(
                    MinterHelper.prefix_remove(self.reward_address)
                ),
                'owner_address': bytes.fromhex(
                    MinterHelper.prefix_remove(self.owner_address)
                )
            }
        })

        return struct

    @classmethod
    def _structure_to_kwargs(cls, structure):
        """ Prepare decoded structure data to instance kwargs. """

        kwargs = super()._structure_to_kwargs(structure)

        # Convert data values to verbose.
        # Data will be passed as additional kwarg
        kwargs['data'].update({
            'pub_key': MinterHelper.prefix_add(
                kwargs['data']['pub_key'].hex(), PREFIX_PUBKEY
            ),
            'reward_address': MinterHelper.prefix_add(
                kwargs['data']['reward_address'].hex(), PREFIX_ADDR
            ),
            'owner_address': MinterHelper.prefix_add(
                kwargs['data']['owner_address'].hex(), PREFIX_ADDR
            )
        })

        # Populate data key values as kwargs
        kwargs.update(kwargs['data'])

        return kwargs

    @classmethod
    def _data_from_raw(cls, raw_data):
        """ Parent method implementation """
        return {
            'pub_key': raw_data[0],
            'reward_address': raw_data[1],
            'owner_address': raw_data[2]
        }
