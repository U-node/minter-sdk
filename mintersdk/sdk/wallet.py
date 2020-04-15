"""
@author: Roman Matusevich
"""
import hashlib
import hmac

import sslcrypto
from mnemonic.mnemonic import Mnemonic
from mintersdk import MinterHelper, PREFIX_PUBKEY, PREFIX_ADDR


class MinterWallet(object):
    """
    Minter wallet class
    """

    # Amount of entropy bits (BIP44)
    entropy_bits = 128

    # Address path for creating wallet from the seed (BIP44)
    seed_address_path = "m/44'/60'/0'/0/0"

    # Master seed
    master_seed = b'Bitcoin seed'

    # Curve data
    curve = sslcrypto.ecc.get_curve('secp256k1')
    pub_key_len = curve._backend.public_key_length

    @classmethod
    def create(cls, mnemonic=None):
        """
        Create Minter wallet
        Args:
            mnemonic (str): Mnemonic phrase
        Returns:
            dict
        """

        # Create mnemonic phrase if None
        if not mnemonic:
            _mnemonic = Mnemonic(language='english')
            mnemonic = _mnemonic.generate(cls.entropy_bits)

        if len(mnemonic.split(' ')) != 12:
            raise Exception('Mnemonic phrase should have 12 words.')

        # Mnemonic to seed (bytes)
        seed = Mnemonic.to_seed(mnemonic, '')

        # Generate master key (key, hmac_key) from master seed
        _I = hmac.new(cls.master_seed, seed, hashlib.sha512).hexdigest()
        master_key = (int(_I[:64], 16), bytes.fromhex(_I[64:]))

        # Get child keys from master key by path
        keys = cls.from_path(
            root_key=master_key, path=cls.seed_address_path
        )

        # Get private key
        private_key = keys[-1][0].to_bytes(length=32, byteorder='big').hex()
        # Get public key from private
        public_key = cls.get_public_from_private(private_key)
        # Get address from public key
        address = cls.get_address_from_public_key(public_key)

        return {
            'address': address,
            'private_key': private_key,
            'mnemonic': mnemonic,
            'seed': seed.hex()
        }

    @classmethod
    def get_public_from_private(cls, private_key):
        """
        Get public key from private key
        Args:
            private_key (str): hex bytes of private key
        Returns:
            str
        """
        # Get public key from private
        public_key = cls.curve.private_to_public(
            int(private_key, 16).to_bytes(length=32, byteorder='big')
        )
        public_key = public_key.hex()[2:]

        return MinterHelper.prefix_add(public_key, PREFIX_PUBKEY)

    @classmethod
    def get_address_from_public_key(cls, public_key):
        """
        Args:
            public_key (str)
        Returns:
            str
        """
        # Create keccak hash
        _keccak = MinterHelper.keccak_hash(
            bytes.fromhex(MinterHelper.prefix_remove(public_key))
        )

        return MinterHelper.prefix_add(_keccak[-40:], PREFIX_ADDR)

    @staticmethod
    def parse_path(path):
        """
        Parsing seed address path.
        Method was ported from 'two1.bitcoin.crypto'
        Args:
            path (str): Seed address path
        Returns:
            list
        """
        if isinstance(path, str):
            # Remove trailing "/"
            p = path.rstrip("/").split("/")
        elif isinstance(path, bytes):
            p = path.decode('utf-8').rstrip("/").split("/")
        else:
            p = list(path)

        return p

    @classmethod
    def from_parent(cls, parent_key, index):
        """
        Generate child private key from parent private key.
        Method was ported from 'two1.bitcoin.crypto'.
        Method is suitable only for private keys. To use full functionality,
        you should install 'two1' package.
        Args:
            parent_key (tuple(int, bytes)): Tuple of key and hmac_key
            index (int): Child index
        Returns:
            tuple(int, bytes): Child key
        """

        if index < 0 or index > 0xffffffff:
            raise ValueError("index is out of range: 0 <= index <= 2**32 - 1")

        # Get curve n parameter.
        curve_n = int(cls.curve.params['n'])

        # Unpack parent key
        parent_key, hmac_key = parent_key

        if index & 0x80000000:
            hmac_data = b'\x00' + parent_key.to_bytes(length=32, byteorder='big')
        else:
            # Create default curve public key from private
            public_key = cls.curve.private_to_public(
                parent_key.to_bytes(length=32, byteorder='big')
            )

            # Get public key coordinates
            x, y = cls.curve.decode_public_key(public_key)
            x = int.from_bytes(x, byteorder='big')
            y = int.from_bytes(y, byteorder='big')

            # Generate hmac data
            hmac_data = (
                bytes([(y & 0x1) + 0x02]) +
                x.to_bytes(cls.pub_key_len, 'big')
            )
        hmac_data += index.to_bytes(length=4, byteorder='big')

        I = hmac.new(hmac_key, hmac_data, hashlib.sha512).digest()
        Il, Ir = I[:32], I[32:]

        parse_Il = int.from_bytes(Il, 'big')
        if parse_Il >= curve_n:
            return None

        child_key = (parse_Il + parent_key) % curve_n
        if child_key == 0:
            # Incredibly unlucky choice
            return None

        return child_key, Ir

    @classmethod
    def from_path(cls, root_key, path):
        """
        Generate keys from path.
        Method was ported from 'two1.bitcoin.crypto'
        Args:
            root_key (tuple(int, bytes)): Tuple of key and hmac_key
            path (str): Seed address path
        Returns:
            list(tuple(int, bytes)): List of tuples (key, hmac_key)
        """
        p = cls.parse_path(path)

        if p[0] == "m":
            p = p[1:]

        keys = [root_key]
        for i in p:
            if isinstance(i, str):
                hardened = i[-1] == "'"
                index = int(i[:-1], 0) | 0x80000000 if hardened else int(i, 0)
            else:
                index = i
            k = keys[-1]

            keys.append(cls.from_parent(parent_key=k, index=index))

        return keys
