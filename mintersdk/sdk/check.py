import rlp
import binascii
import hashlib
from mintersdk import MinterHelper, MinterConvertor, MinterPrefix
from mintersdk.sdk import ECDSA
from mintersdk.sdk.wallet import MinterWallet


class MinterCheck(object):
    """
    Minter check class
    Create new check or decode existing
    """

    def __init__(self, nonce, due_block, coin, value, passphrase=None,
                 chain_id=1, **kwargs):
        """
        Args:
            nonce (int)
            due_block (int)
            coin (str)
            value (float)
            passphrase (str)
            chain_id (int)
        """

        self.nonce = nonce
        self.due_block = due_block
        self.coin = coin
        self.value = value
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

        return MinterHelper.hex2bin(signature)

    def sign(self, private_key):
        """
        Sign check
        Args:
            private_key (str)
        """

        if not self.passphrase:
            raise ValueError('Passphrase should be not empty string')

        # Prepare structure
        # It contains nonce, chain_id, due_block, coin, value, lock, v, r, s
        # lock, v, r, s appended later in code
        structure = [
            int(binascii.hexlify(str(self.nonce).encode()), 16),
            self.chain_id,
            self.due_block,
            MinterConvertor.encode_coin_name(self.coin),
            MinterConvertor.convert_value(value=self.value, to='pip')
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
        check = binascii.hexlify(rlp.encode(structure))

        return MinterPrefix.CHECK + check.decode()

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
        address = MinterPrefix.remove_prefix(
            string=address,
            prefix=MinterPrefix.ADDRESS
        )
        address = MinterHelper.hex2bin(address)
        address_hash = cls.__hash(data=[address])

        # Create SHA256 from passphrase
        sha = hashlib.sha256()
        sha.update(passphrase.encode())
        passphrase = sha.hexdigest()

        # Get signature
        signature = ECDSA.sign(message=address_hash, private_key=passphrase)

        return binascii.hexlify(cls.__lockfromsignature(signature)).decode()

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
        rawcheck = MinterPrefix.remove_prefix(
            string=rawcheck,
            prefix=MinterPrefix.CHECK
        )
        rawcheck = binascii.unhexlify(rawcheck)
        decoded = rlp.decode(rawcheck)

        # Create MinterCheck instance
        kwargs = {
            'nonce': int(decoded[0].decode()),
            'chain_id': MinterHelper.bin2int(decoded[1]),
            'due_block': MinterHelper.bin2int(decoded[2]),
            'coin': MinterConvertor.decode_coin_name(decoded[3]),
            'value': MinterConvertor.convert_value(
                value=MinterHelper.bin2int(decoded[4]),
                to='bip'
            ),
            'lock': binascii.hexlify(decoded[5]).decode(),
            'signature': {
                'v': MinterHelper.bin2int(decoded[6]),
                'r': MinterHelper.bin2hex(decoded[7]),
                's': MinterHelper.bin2hex(decoded[8])
            }
        }
        check = MinterCheck(**kwargs)

        # Recover owner address
        msg_hash = cls.__hash(data=[
            int(binascii.hexlify(str(check.nonce).encode()), 16),
            check.chain_id,
            check.due_block,
            MinterConvertor.encode_coin_name(check.coin),
            MinterConvertor.convert_value(value=check.value, to='pip'),
            MinterHelper.hex2bin(check.lock)
        ])
        public_key = ECDSA.recover(msg_hash, list(check.signature.values()))
        public_key = MinterPrefix.PUBLIC_KEY + public_key

        check.owner = MinterWallet.get_address_from_public_key(public_key)

        return check
