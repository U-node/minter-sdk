"""
@author: Roman Matusevich
"""
import hashlib

import rlp
from mintersdk import MinterHelper, PREFIX_CHECK, PREFIX_PUBKEY
from mintersdk.sdk import ECDSA
from mintersdk.sdk.wallet import MinterWallet


class MinterCheck(object):
    """
    Minter check class
    Create new check or decode existing
    """

    def __init__(self, nonce, due_block, coin, value, gas_coin,
                 passphrase=None, chain_id=1, **kwargs):
        """
        Args:
            nonce (int)
            due_block (int)
            coin (str)
            value (float)
            gas_coin (str): Gas coin symbol
            passphrase (str)
            chain_id (int)
        """

        self.nonce = nonce
        self.due_block = due_block
        self.coin = coin.upper()
        self.value = value
        self.gas_coin = gas_coin.upper()
        self.passphrase = passphrase
        self.chain_id = chain_id

        for attr, value in kwargs.items():
            setattr(self, attr, value)

    @staticmethod
    def __hash(data):
        """
        Create service hash by RLP encoding and getting keccak hash from
        rlp result
        Args:
            data (list)
        Returns:
            hash (str)
        """
        return MinterHelper.keccak_hash(rlp.encode(data))

    @staticmethod
    def __lockfromsignature(signature):
        """
        Create lock from signature
        Args:
            signature (list): [v, r, s] list
        Returns:
            bytes
        """

        v, r, s = signature
        v = '00' if v == 27 else '01'
        signature = format(r, 'x').zfill(64) + format(s, 'x').zfill(64) + v

        return bytes.fromhex(signature)

    def sign(self, private_key):
        """
        Sign check
        Args:
            private_key (str)
        """

        if not self.passphrase:
            raise ValueError('Passphrase should be not empty string')

        # Prepare structure
        # It contains nonce, chain_id, due_block, coin, value, gas_coin,
        # lock, v, r, s.
        # lock, v, r, s appended later in code
        structure = [
            int(str(self.nonce).encode().hex(), 16),
            self.chain_id,
            self.due_block,
            MinterHelper.encode_coin_name(self.coin),
            MinterHelper.to_pip(self.value),
            MinterHelper.encode_coin_name(self.gas_coin)
        ]

        # Create msg hash
        msg_hash = self.__hash(structure)

        # SHA256 from passphrase
        sha = hashlib.sha256()
        sha.update(self.passphrase.encode())
        passphrase = sha.hexdigest()

        # Create lock from signature
        self.lock = self.__lockfromsignature(
            signature=ECDSA.sign(message=msg_hash, private_key=passphrase)
        )

        # Re-create msg hash with adding lock to structure
        structure.append(self.lock)
        msg_hash = self.__hash(structure)

        # Re-create signature, add it to check attrs and to structure
        signature = ECDSA.sign(message=msg_hash, private_key=private_key)
        self.signature = {
            'v': signature[0],
            'r': format(signature[1], 'x'),
            's': format(signature[2], 'x')
        }
        structure += signature

        # Get RLP, which will be the check
        check = rlp.encode(structure).hex()

        return MinterHelper.prefix_add(check, PREFIX_CHECK)

    @classmethod
    def proof(cls, address, passphrase):
        """
        Create proof
        Args:
            address (str)
            passphrase (str)
        Returns:
            str
        """

        # Get address hash
        address = MinterHelper.prefix_remove(address)
        address = bytes.fromhex(address)
        address_hash = cls.__hash(data=[address])

        # Create SHA256 from passphrase
        sha = hashlib.sha256()
        sha.update(passphrase.encode())
        passphrase = sha.hexdigest()

        # Get signature
        signature = ECDSA.sign(message=address_hash, private_key=passphrase)

        return cls.__lockfromsignature(signature).hex()

    @classmethod
    def from_raw(cls, rawcheck):
        """
        Create check instance from raw check
        Args:
            rawcheck (str)
        Returns:
            MinterCheck
        """

        # Remove check prefix and RLP decode it
        rawcheck = MinterHelper.prefix_remove(rawcheck)
        rawcheck = bytes.fromhex(rawcheck)
        decoded = rlp.decode(rawcheck)

        # Create MinterCheck instance
        kwargs = {
            'nonce': int(decoded[0].decode()),
            'chain_id': int.from_bytes(decoded[1], 'big'),
            'due_block': int.from_bytes(decoded[2], 'big'),
            'coin': MinterHelper.decode_coin_name(decoded[3]),
            'value': MinterHelper.to_bip(int.from_bytes(decoded[4], 'big')),
            'gas_coin': MinterHelper.decode_coin_name(decoded[5]),
            'lock': decoded[6].hex(),
            'signature': {
                'v': int.from_bytes(decoded[7], 'big'),
                'r': decoded[8].hex(),
                's': decoded[9].hex()
            }
        }
        check = MinterCheck(**kwargs)

        # Recover owner address
        msg_hash = cls.__hash(data=[
            int(str(check.nonce).encode().hex(), 16),
            check.chain_id,
            check.due_block,
            MinterHelper.encode_coin_name(check.coin),
            MinterHelper.to_pip(check.value),
            MinterHelper.encode_coin_name(check.gas_coin),
            bytes.fromhex(check.lock)
        ])
        public_key = ECDSA.recover(msg_hash, tuple(check.signature.values()))
        public_key = MinterHelper.prefix_add(public_key, PREFIX_PUBKEY)

        check.owner = MinterWallet.get_address_from_public_key(public_key)

        return check
