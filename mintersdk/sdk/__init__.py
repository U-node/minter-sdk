"""
@author: Roman Matusevich
"""
import sslcrypto


class ECDSA:
    """
    ECDSA class
    """

    # Curve data
    curve = sslcrypto.ecc.get_curve('secp256k1')
    pub_key_len = curve._backend.public_key_length

    @classmethod
    def sign(cls, message, private_key):
        """
        Args:
            message (string): message to sign
            private_key (string): private_key
        Returns:
            list(int)
        """

        # Create signature
        signature = cls.curve.sign(
            data=bytes.fromhex(message), private_key=bytes.fromhex(private_key),
            recoverable=True, hash=None
        )
        v = signature[0]
        r = int.from_bytes(signature[1:cls.pub_key_len+1], byteorder='big')
        s = int.from_bytes(signature[cls.pub_key_len+1:], byteorder='big')

        return [v, r, s]

    @classmethod
    def recover(cls, message, vrs):
        """
        Args:
            message (string): message
            vrs (tuple): tuple of v, r, s (r, s in hex)
        Returns:
            str
        """

        # Create signature
        signature = (
            vrs[0].to_bytes(length=1, byteorder='big') +
            int(vrs[1], 16).to_bytes(
                length=cls.pub_key_len, byteorder='big'
            ) +
            int(vrs[2], 16).to_bytes(
                length=cls.pub_key_len, byteorder='big'
            )
        )

        # Get raw recover of public key.
        pub_key_raw = cls.curve.recover(
            signature=signature, data=bytes.fromhex(message), hash=None
        )

        # Convert public key to hex electrum format
        x, y = cls.curve.decode_public_key(pub_key_raw)
        pub_key = x.hex() + y.hex()

        return pub_key
