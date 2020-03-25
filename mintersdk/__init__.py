import os
import random
import decimal
import string
import hashlib
import sha3

import pyqrcode
from deprecated import deprecated


# Number of PIP in 1 BIP
PIP = 1000000000000000000

# Prefixes
PREFIX_ADDR = 'Mx'
PREFIX_PUBKEY = 'Mp'
PREFIX_CHECK = 'Mc'
PREFIX_TX = 'Mt'


@deprecated("Use 'to_bip', 'to_pip' shortcuts or MinterHelper methods")
class MinterConvertor:
    """
    Class contains different converters
    """

    # PIP in BIP
    DEFAULT = 1000000000000000000

    @classmethod
    def convert_value(cls, value, to, prec=33):
        """
        Convert values from/to pip/bip.
        Args:
            value (string|int|Decimal|float): value to convert
            to (string): coin to convert value to
            prec (int): decimal context precision (decimal number length)
        Returns:
            int|Decimal
        """
        # Get default decimal context
        context = decimal.getcontext()
        # Set temporary decimal context for calculation
        decimal.setcontext(
            decimal.Context(prec=prec, rounding=decimal.ROUND_DOWN)
        )

        # PIP in BIP in Decimal
        default = decimal.Decimal(str(cls.DEFAULT))
        # Value in Decimal
        value = decimal.Decimal(str(value))

        # Make conversion
        if to == 'pip':
            value = int(value * default)
        elif to == 'bip':
            value /= default

        # Reset decimal context to default
        decimal.setcontext(context)

        return value

    @classmethod
    def encode_coin_name(cls, symbol):
        """
        Add nulls to coin name
        Args:
            symbol (string): coin symbol
        Returns:
            string
        """
        return symbol + chr(0) * (10 - len(symbol))

    @classmethod
    def decode_coin_name(cls, symbol):
        """
        Args:
            symbol (bytes|str)
        Returns:
            string
        """

        if hasattr(symbol, 'decode'):
            symbol = symbol.decode()

        return symbol.replace(chr(0), '')


class MinterHelper:
    """
    Class which contains different helpers
    """

    @staticmethod
    def keccak_hash(data, digest_bits=256):
        """
        Create Keccak hash.
        Args:
            data (bytes)
            digest_bits (int)
        Returns:
            hex (string)
        """

        if digest_bits == 256:
            khash = sha3.keccak_256()
        else:
            raise NotImplementedError

        khash.update(data)

        return khash.hexdigest()

    @staticmethod
    @deprecated('Unnecessary method')
    def hex2bin(string):
        return bytes.fromhex(string)

    @classmethod
    def hex2bin_recursive(cls, _dict):
        """
        Recursively convert hexdigit dict values to bytes.
        Args:
            _dict (dict)
        Returns:
            dict
        """

        def ctype_xdigit(s):
            """
            Checks if all of the characters in "s" are hexadecimal 'digits'.
            Args:
                s (string): string to check
            """
            return all(c in string.hexdigits for c in s)

        for k, v in _dict.items():
            if type(v) == dict:
                cls.hex2bin_recursive(v)
            elif type(v) == str and ctype_xdigit(v):
                try:
                    _dict[k] = bytes.fromhex(v)
                except ValueError:
                    pass

        return _dict

    @staticmethod
    @deprecated('Unnecessary method')
    def bin2hex(bts):
        return bts.hex()

    @staticmethod
    @deprecated('Unnecessary method')
    def bin2int(number):
        return int.from_bytes(number, 'big')

    @staticmethod
    def get_validator_address(pub_key, upper=True):
        """
        Get validator address from it's pub key (Mp...).
        Validator address is used in signing blocks.
        Args:
            pub_key (string): candidate public key (Mp....)
            upper (bool)
        Returns:
            string, validator address
        """

        pub_key = bytes.fromhex(MinterHelper.prefix_remove(pub_key))
        vaddress = hashlib.sha256(pub_key).hexdigest()[:40]

        return vaddress.upper() if upper else vaddress

    @staticmethod
    def generate_qr(text, fn=None, path='', error='H', version=None, mode=None,
                    output='svg', module_color='black', background='white',
                    quiet_zone=4):
        """
        Generate QR code from text and save to file.
        Detailed documentation for `pyqrcode` package can be found
        here: https://pythonhosted.org/PyQRCode/index.html
        Args:
            text (str): Text, that should be encoded to QR
            fn (str): Filename for generated QR.
                      If not provided random filename is generated.
            path (str): Path to save generate QR
            error (str|int): The error parameter sets the error correction
                             level of the code.
                             Each level has an associated name given by a
                             letter: L, M, Q, or H;
                             each level can correct up to 7, 15, 25, or 30
                             percent of the data respectively.
            version (int): The version parameter specifies the size and data
                           capacity of the code.
                           Versions are any integer between 1 and 40
            mode (str): The mode param sets how the contents will be encoded.
                        Three of the four possible encodings are available.
                        By default, the object uses the most efficient
                        encoding for the contents. You can override this
                        behavior by setting this parameter.
            output (str): Render modes. Available: text|terminal|svg.
                          In `text`|`terminal` modes QR code is printed,
                          `svg` mode saves QR code to file `fn` to path `path`.
            module_color (str): String color of QR code data.
                                Is used only for `terminal` and `svg` modes.
            background (str): String color of QR code background.
                              Is used only for `terminal` and `svg` modes.
            quiet_zone (int): QR code quiet zone.
        Returns:
            fnpath (str): Path to generated QR
        """

        # Generate QR code object
        qrcode = pyqrcode.create(content=text, error=error, version=version,
                                 mode=mode)

        # Render QR code depending on `output` param
        if output == 'text':
            print(qrcode.text(quiet_zone=quiet_zone))
        elif output == 'terminal':
            print(
                qrcode.terminal(
                    module_color=module_color, background=background,
                    quiet_zone=quiet_zone
                )
            )
        elif output == 'svg':
            # Generate filename, if not provided
            if not fn:
                fn = text + str(random.randint(10000, 99999))
                fn = hashlib.sha256(fn.encode()).hexdigest()[:10]
            fnpath = os.path.join(path, fn + '.svg')

            # Save QR code to file
            qrcode.svg(file=fnpath, module_color=module_color,
                       background=background, quiet_zone=quiet_zone)

            return fnpath
        else:
            raise Exception('Wrong QR code render mode')

    @staticmethod
    def bytes_len(value, encoding='utf-8'):
        """
        Count bytes length
        Args:
            value (str|bytes)
            encoding (str)
        """
        if type(value) is str:
            value = bytes(value, encoding=encoding)

        return len(value)

    @staticmethod
    def encode_coin_name(symbol):
        """
        Add nulls to coin name
        Args:
            symbol (string): coin symbol
        Returns:
            string
        """
        return symbol + chr(0) * (10 - len(symbol))

    @staticmethod
    def decode_coin_name(symbol):
        """
        Args:
            symbol (bytes|str)
        Returns:
            string
        """

        if hasattr(symbol, 'decode'):
            symbol = symbol.decode()

        return symbol.replace(chr(0), '')

    @staticmethod
    def to_pip(value):
        """
        Convert BIPs to PIPs.
        Always cast value to str, due to float behaviour:
            Decimal(0.1) = Decimal('0.10000000000004524352345234')
            Decimal('0.1') = Decimal('0.1')
        Args:
            value (str|float|int): value in BIP
        Returns:
            int
        """
        return int(decimal.Decimal(str(value)) * decimal.Decimal(PIP))

    @staticmethod
    def to_bip(value):
        """
        Convert PIPs to BIPs.
        Use dynamic Decimal precision, depending on value length.
        Args:
            value (int|str): value in PIP
        Returns:
            Decimal
        """
        # Check if value is correct PIP value
        if type(value) not in [int, str]:
            raise ValueError(f"{value} should be 'int' or 'str of digits'")
        if type(value) is str and not value.isdigit():
            raise ValueError(f'{value} is not correct PIP value')

        # Get default decimal context
        context = decimal.getcontext()
        # Set temporary decimal context for calculation
        decimal.setcontext(
            decimal.Context(prec=len(str(value)), rounding=decimal.ROUND_DOWN)
        )

        # Convert value
        value = decimal.Decimal(value) / decimal.Decimal(PIP)

        # Reset decimal context to default
        decimal.setcontext(context)

        return value

    @staticmethod
    def prefix_add(value, prefix):
        if prefix not in [PREFIX_ADDR, PREFIX_PUBKEY, PREFIX_CHECK, PREFIX_TX]:
            raise ValueError(f"Unknown prefix '{prefix}'")
        return prefix + value

    @staticmethod
    def prefix_remove(value):
        value = value.replace(PREFIX_ADDR, '')
        value = value.replace(PREFIX_PUBKEY, '')
        value = value.replace(PREFIX_CHECK, '')
        value = value.replace(PREFIX_TX, '')

        return value


@deprecated("Deprecated. Use 'MinterHelper' class instead")
class MinterPrefix:
    """
    Class with minter prefixes and operations with them.
    """

    # Minter wallet address prefix
    ADDRESS = 'Mx'

    # Minter public key prefix
    PUBLIC_KEY = 'Mp'

    # Minter redeem check prefix
    CHECK = 'Mc'

    # Minter transaction prefix
    TRANSACTION = 'Mt'

    @staticmethod
    def remove_prefix(string, prefix):
        return string.replace(prefix, '')
