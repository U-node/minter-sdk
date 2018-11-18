import decimal
import binascii
import string
import hashlib
from Crypto.Hash import keccak


class MinterConvertor:
    """
    Class contains different convertors
    """
    
    # PIP in BIP
    DEFAULT = '1000000000000000000';
    
    @classmethod
    def convert_value(cls, value, to):
        """
        Convert values from/to pip/bip.
            @param value|string: value to convert
            @param to|string: coin to convert value to 
            @return: int|float
        """
        if to == 'pip':
            return int(MinterHelper.pybcmul(value, cls.DEFAULT))
        elif to == 'bip':
            return float(MinterHelper.pybcdiv(value, cls.DEFAULT))
        
    @classmethod
    def convert_coin_name(cls, symbol):
        """
        Add nulls to coin name
            @param symbol|string: coin symbol
            @return: string
        """
        return symbol + chr(0)*(10 - len(symbol))


class MinterHelper:
    """
    Class which contains different helpers
    """
    
    @classmethod
    def pybcmul(cls, value, miltiplyer, precision=25):
        """
        Implementation of PHP bcmul.
        We need to implementation bcmul php function, because firstly sdk was written in PHP.
        Thats why we change decimal roundings.
        """
        
        decimal.getcontext().rounding = decimal.ROUND_DOWN
        decimal.getcontext().prec = precision
        
        return decimal.Decimal(str(value)) * decimal.Decimal(str(miltiplyer))
    
    @classmethod
    def pybcdiv(cls, value, divider, precision=25):
        """
        Implementation of PHP bcdiv.
        We need to implementation bcdiv php function, because firstly sdk was written in PHP.
        Thats why we change decimal roundings.
        """
        
        decimal.getcontext().rounding = decimal.ROUND_DOWN
        decimal.getcontext().prec = precision
        
        return decimal.Decimal(str(value)) / decimal.Decimal(str(divider))
    
    @classmethod
    def pybcadd(cls, addendf, addends, precision=25):
        """
        Implementation of PHP bcadd.
        We need to implementation bcadd php function, because firstly sdk was written in PHP.
        Thats why we change decimal roundings.
        """
        
        decimal.getcontext().rounding = decimal.ROUND_DOWN
        decimal.getcontext().prec = precision
        
        return decimal.Decimal(str(addendf)) + decimal.Decimal(str(addends))
    
    @classmethod
    def pybcsub(cls, addendf, addends, precision=25):
        """
        Implementation of PHP bcsub.
        We need to implementation bcadd php function, because firstly sdk was written in PHP.
        Thats why we change decimal roundings.
        """
        
        decimal.getcontext().rounding = decimal.ROUND_DOWN
        decimal.getcontext().prec = precision
        
        return decimal.Decimal(str(addendf)) - decimal.Decimal(str(addends))
    
    @classmethod
    def keccak_hash(cls, data, digest_bits=256):
        """
        Create Keccak hash.
            @param data|bytes
            @param digest_bits|int 
            @return: hex string
        """
        
        khash = keccak.new(digest_bits=digest_bits)
        khash.update(data)
        
        return khash.hexdigest()
    
    @classmethod
    def hex2bin_recursive(cls, _dict):
        """
        hex2bin part - analog of PHP hex2bin. 
        (The hex2bin() function converts a string of hexadecimal values to ASCII characters.)
        In Python it can be done by binascii.unhexlify().
        Recursive hex2bin for dict.
            @param _dict|dict:
            @return: dict
        """
        
        def ctype_xdigit(s):
            """
            Checks if all of the characters in "s" are hexadecimal 'digits'.
                @param s|string: string to check
            """
            return all(c in string.hexdigits for c in s)
            
        
        for k, v in _dict.items():
            if type(v) == dict:
                cls.hex2bin_recursive(v)
            elif type(v) == str and ctype_xdigit(v):
                _dict[k] = binascii.unhexlify(v)
                
        return _dict
    
    @classmethod
    def get_validator_address(cls, pub_key, upper=True):
        """
        Get validator address from it's pub key (Mp...).
        Validator address is used in signing blocks.
            @param pub_key|string: candidate public key (Mp....)
            @return: string, validator address
        """
        
        pub_key = binascii.unhexlify(
                        MinterPrefix.remove_prefix(pub_key, MinterPrefix.PUBLIC_KEY)
                    )
        
        vaddress = hashlib.sha256(pub_key).hexdigest()[:40]
        
        return vaddress.upper() if upper else vaddress 
    
    
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