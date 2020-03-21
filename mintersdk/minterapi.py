"""
@author: Roman
"""
import requests
import json

from deprecated import deprecated
from mintersdk import MinterConvertor


class MinterAPI(object):
    """
    Base MinterAPI class
    """
    # API host
    api_url = ''

    # Timeout connecting to host
    connect_timeout = 1

    # Timeout reading from host
    read_timeout = 3

    # Default request headers
    headers = {
      'Content-Type': 'application/json'
    }

    def __init__(self, api_url, **kwargs):
        """
        Args:
            api_url (str): API host, e.g. http://localhost/api/
            kwargs: Any other attributes you need
                    Predefined kwargs:
                        - connect_timeout (float|int)
                        - read_timeout (float|int)
                        - headers (dict)

        """
        self.api_url = api_url
        if self.api_url[-1] != '/':
            self.api_url += '/'

        for name, value in kwargs.items():
            setattr(self, name, value)

    def get_status(self):
        """ Get node status """
        return self._request(command='status')

    def get_candidate(self, public_key, height=None, pip2bip=False):
        """
        Get candidate
        Args:
            public_key (string): candidate public key
            height (int): block height,
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        response = self._request(
            command='candidate',
            params={'pub_key': public_key, 'height': height}
        )

        if pip2bip:
            return self.__response_processor(
                data=response,
                funcs=[(self.__pip_to_bip, {'exclude': ['commission']})],
            )

        return response

    def get_validators(self, height=None, page=None, limit=None):
        """
        Get validators list
        Args:
            height (int): get validators on specified block height
            page (int|None): page number
            limit (int|None): items per page
        """
        return self._request(
            command='validators',
            params={'height': height, 'page': page, 'perPage': limit}
        )

    def get_addresses(self, addresses, height=None, pip2bip=False):
        """
        Returns addresses balances
        Args:
            addresses (list[str]): Addresses list
            height (int|None): Block height
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        response = self._request(
            command='addresses',
            params={'addresses': json.dumps(addresses), 'height': height}
        )

        if pip2bip:
            return self.__response_processor(
                data=response, funcs=[self.__pip_to_bip]
            )

        return response

    def get_balance(self, address, height=None, pip2bip=False):
        """
        Get balance by address
        Args:
            address (string): wallet address
            height (int): block height
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        response = self._request(
            command='address', params={'address': address, 'height': height}
        )

        if pip2bip:
            return self.__response_processor(
                data=response, funcs=[self.__pip_to_bip]
            )

        return response

    def get_nonce(self, address):
        """
        Nonce - int, used for prevent transaction reply
        Args:
            address (string): wallet address
        """

        balance = self.get_balance(address)
        nonce = balance['result']['transaction_count'] + 1

        return nonce

    def send_transaction(self, tx):
        """
        Send transaction
        Args:
            tx (string): signed transaction to send
        """
        return self._request(
            command='send_transaction', params={'tx': '0x' + tx}
        )

    def get_transaction(self, tx_hash, pip2bip=False):
        """
        Get transaction info
        Args:
            tx_hash (string): transaction hash
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        response = self._request(
            command='transaction', params={'hash': '0x' + tx_hash}
        )

        if pip2bip:
            return self.__response_processor(
                data=response,
                funcs=[(self.__pip_to_bip, {'exclude': ['commission']})]
            )

        return response

    def get_block(self, height, pip2bip=False):
        """
        Get block data at given height
        Args:
            height (int): block height
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        response = self._request(command='block', params={'height': height})

        if pip2bip:
            return self.__response_processor(
                data=response, funcs=[self.__pip_to_bip]
            )

        return response

    def get_latest_block_height(self):
        """
        Get latest block height
        """
        return self.get_status()['result']['latest_block_height']

    def get_events(self, height, pip2bip=False):
        """
        Get events at given height
        Args:
            height (int): block height
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        response = self._request(command='events', params={'height': height})

        if pip2bip:
            return self.__response_processor(
                data=response, funcs=[self.__pip_to_bip]
            )

        return response

    def get_candidates(self, height=None, include_stakes=False, pip2bip=False):
        """
        Get candidates
        Args:
            height (int): block height
            include_stakes (bool)
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        response = self._request(
            command='candidates',
            params={
                'height': height,
                'include_stakes': str(include_stakes).lower()
            }
        )

        if pip2bip:
            return self.__response_processor(
                data=response,
                funcs=[(self.__pip_to_bip, {'exclude': ['commission']})]
            )

        return response

    def get_coin_info(self, symbol, height=None, pip2bip=False):
        """
        Get information about coin
        Args:
            symbol (string): coin name
            height (int): block height
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        response = self._request(
            command='coin_info',
            params={'symbol': symbol.upper(), 'height': height}
        )

        if pip2bip:
            return self.__response_processor(
                data=response, funcs=[self.__pip_to_bip]
            )

        return response

    def estimate_coin_sell(self, coin_to_sell, value_to_sell, coin_to_buy,
                           height=None, pip2bip=False):
        """
        Return estimate of sell coin transaction
        Args:
            coin_to_sell (string): coin name to sell
            value_to_sell (string|int): Amount of coins to sell in PIP.
                    Provide `value_to_sell` in PIP, if `pip2bip` False.
                    Provide `value_to_sell` in BIP, if `pip2bip` True.
            coin_to_buy (string): coin name to buy
            height (int): block height
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        # Convert `value_to_sell` to PIP, if needed
        if pip2bip:
            value_to_sell = MinterConvertor.convert_value(
                value=value_to_sell, to='pip'
            )

        # Get default response
        response = self._request(
            command='estimate_coin_sell',
            params={
                'coin_to_sell': coin_to_sell.upper(),
                'value_to_sell': value_to_sell,
                'coin_to_buy': coin_to_buy.upper(),
                'height': height
            }
        )

        # Convert response values from PIP to BIP, if needed
        if pip2bip:
            return self.__response_processor(
                data=response, funcs=[self.__pip_to_bip]
            )

        return response

    def estimate_coin_sell_all(self, coin_to_sell, value_to_sell, coin_to_buy,
                               height=None, pip2bip=False):
        """
        Return estimate of sell all coin transaction.
        Args:
            coin_to_sell (string): coin name to sell
            value_to_sell (string|int): Amount of coins to sell in PIP.
                    Provide `value_to_sell` in PIP, if `pip2bip` False.
                    Provide `value_to_sell` in BIP, if `pip2bip` True.
            coin_to_buy (string): coin name to buy
            height (int): block height
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        # Convert `value_to_sell` to PIP, if needed
        if pip2bip:
            value_to_sell = MinterConvertor.convert_value(
                value=value_to_sell, to='pip'
            )

        # Get default response
        response = self._request(
            command='estimate_coin_sell_all',
            params={
                'coin_to_sell': coin_to_sell.upper(),
                'value_to_sell': value_to_sell,
                'coin_to_buy': coin_to_buy.upper(),
                'height': height
            }
        )

        # Convert response values from PIP to BIP, if needed
        if pip2bip:
            return self.__response_processor(
                data=response, funcs=[self.__pip_to_bip]
            )

        return response

    def estimate_coin_buy(self, coin_to_sell, value_to_buy, coin_to_buy,
                          height=None, pip2bip=False):
        """
        Return estimate of buy coin transaction
        Args:
            coin_to_sell (string): coin name to sell
            value_to_buy (string): Amount of coins to buy in PIP.
                    Provide `value_to_buy` in PIP, if `pip2bip` False.
                    Provide `value_to_buy` in BIP, if `pip2bip` True.
            coin_to_buy (string): coin name to buy
            height (int): block height
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        # Convert `value_to_buy` to PIP, if needed
        if pip2bip:
            value_to_buy = MinterConvertor.convert_value(
                value=value_to_buy, to='pip'
            )

        # Get default response
        response = self._request(
            command='estimate_coin_buy',
            params={
                'coin_to_sell': coin_to_sell,
                'value_to_buy': value_to_buy,
                'coin_to_buy': coin_to_buy,
                'height': height
            }
        )

        # Convert response values from PIP to BIP, if needed
        if pip2bip:
            return self.__response_processor(
                data=response, funcs=[self.__pip_to_bip]
            )

        return response

    @deprecated("Please, use 'estimate_tx_commission' instead")
    def estimate_tx_comission(self, tx, height=None):
        """
        Estimate current tx gas.
        Args:
            tx (string): signed transaction
            height (int|None): block height
        """
        if tx[:2] != '0x':
            tx = '0x' + tx

        return self._request(
            command='estimate_tx_commission',
            params={'tx': tx, 'height': height}
        )

    def estimate_tx_commission(self, tx, height=None, pip2bip=False):
        """
        Estimate current tx gas.
        Args:
            tx (string): signed transaction
            height (int|None): block height
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        if tx[:2] != '0x':
            tx = '0x' + tx

        response = self._request(
            command='estimate_tx_commission',
            params={'tx': tx, 'height': height}
        )

        if pip2bip:
            return self.__response_processor(
                data=response, funcs=[self.__pip_to_bip]
            )

        return response

    def get_transactions(self, query, page=None, limit=None, pip2bip=False):
        """
        Get transactions by query.
        Args:
            query (string)
            page (int)
            limit (int)
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        response = self._request(
            command='transactions',
            params={'query': query, 'page': page, 'perPage': limit}
        )

        if pip2bip:
            return self.__response_processor(
                data=response, funcs=[self.__pip_to_bip]
            )

        return response

    def get_unconfirmed_transactions(self, limit=None):
        """
        Get unconfirmed transactions.
        Args:
            limit (int)
        """
        return self._request(
            command='unconfirmed_txs', params={'limit': limit}
        )

    def get_max_gas_price(self, height=None):
        """
        Returns current max gas price.
        Args:
            height (int)
        """
        return self._request(command='max_gas', params={'height': height})

    def get_min_gas_price(self):
        """
        Returns min gas price.
        """
        return self._request(command='min_gas_price')

    def get_missed_blocks(self, public_key, height=None):
        """
        Returns missed blocks by validator public key.
        Args:
            public_key (str): candidate public key
            height (int): block chain height
        """
        return self._request(
            command='missed_blocks',
            params={'pub_key': public_key, 'height': height}
        )

    def get_genesis(self, pip2bip=False):
        """
        Return network genesis.
        Args:
            pip2bip (bool): Convert coin amounts to BIP (default is in PIP)
        """
        response = self._request(command='genesis')
        if pip2bip:
            return self.__response_processor(
                data=response, funcs=[self.__pip_to_bip]
            )
        return response

    def get_network_info(self):
        """ Return node network information. """
        return self._request(command='net_info')

    def _request(self, command, request_type='get', **kwargs):
        """
        Send all requests to API
        Args:
            command (str): API command
            request_type (str): Request type (GET|POST)
            kwargs: requests package arguments
        """
        # Add timeouts if were not set
        if not kwargs.get('timeout', None):
            kwargs['timeout'] = (self.connect_timeout, self.read_timeout)

        # Add headers
        if not kwargs.get('headers', None):
            kwargs['headers'] = self.headers

        # Trying make request
        try:
            url = self.api_url + command

            if request_type == 'get':
                response = requests.get(url, **kwargs)
            elif request_type == 'post':
                response = requests.post(url, **kwargs)
            else:
                response = None

            # Try to get json response and prepare result
            try:
                return self.__response_processor(
                    data=response.json(), funcs=[self.__digits_to_int]
                )
            except Exception as e:
                msg = 'Response parse JSON error: {}; Response is: {}'
                raise Exception(msg.format(e.__str__(), response.text))
        except requests.exceptions.ReadTimeout:
            raise
        except requests.exceptions.ConnectTimeout:
            raise
        except requests.exceptions.ConnectionError:
            raise
        except requests.exceptions.HTTPError:
            raise
        except ValueError:
            raise

    @staticmethod
    def __digits_to_int(value, key, exclude=None):
        """
        Numeric strings to integers converter.
        Used as processor function for '__response_processor()'
        Args:
            exclude (list|None): keys to be excluded
        Returns:
            int|any
        """
        # Combine default exclude list with argument
        exclude_keys = ['tx.type']
        if type(exclude) is list:
            exclude_keys += exclude

        # Convert value
        if type(value) is str and value.isdigit() and \
                (key not in exclude_keys or key is None):
            return int(value)

        return value

    @staticmethod
    def __pip_to_bip(value, key, exclude=None):
        """
        Convert coin amounts integers from PIP to BIP.
        Used as processor function for '__response_processor()'
        Args:
            exclude ([str]): Keys excluded from conversion
        Returns:
            Decimal|int
        """
        # Keys with coin values. Keys' values should be converted
        # from PIP to BIP
        include_keys = [
            'total_stake', 'value', 'bip_value', 'value_to_buy', 'volume',
            'maximum_value_to_sell', 'initial_amount', 'initial_reserve',
            'max_supply', 'stake', 'value_to_sell', 'tx.sell_amount',
            'minimum_value_to_buy', 'tx.return', 'block_reward', 'amount',
            'reserve_balance', 'will_get', 'commission', 'total_bip_stake',
            'will_pay', 'accum_reward', 'total_slashed'
        ]

        # Combine default exclude list with argument
        exclude_keys = []
        if type(exclude) is list:
            exclude_keys += exclude

        # Convert value.
        # Key should be present in 'include_keys' and should be missing
        # in 'exclude_keys' or key is coin symbol.
        # DANGEROUS! We determine if key is coin symbol by checking
        # if key is uppercase or not (should think more about it).
        if type(value) is int and \
                (
                    (key in include_keys and key not in exclude_keys) or
                    key.isupper()
                ):
            return MinterConvertor.convert_value(value=value, to='bip')

        return value

    @staticmethod
    def __response_processor(data, funcs):
        """
        Works only with successful response: response status is 200
        and contains 'result' key.
        Args:
            data (dict): Response text dict (json parsed)
            funcs (list): Functions to be applied to dict values
        Returns:
            dict
        """

        def data_recursive(result, fn):
            """
            Method is used for looping response 'result' until plain
            values are got.
            Then this values are processed by 'fn'.
            Args:
                result (any): 'result' key value from response text
                fn (function|[function, kwargs]): function to process value
            Returns:
                result (any)
            """
            # Unpack fn if list or tuple
            processor = fn
            kwargs = {}
            if type(fn) in [list, tuple]:
                processor, kwargs = fn

            # Go recursion
            if type(result) is list:
                for item in result:
                    data_recursive(item, fn)
            elif type(result) is dict:
                for key, value in result.items():
                    if type(value) in [list, dict]:
                        data_recursive(value, fn)
                    else:
                        result[key] = processor(value, key, **kwargs)
            else:
                return processor(value=result, key=None, **kwargs)

            return result

        # If there is no 'result' key in data, return original data
        if not data.get('result'):
            return data

        # Otherwise apply value processor functions to 'result' key values
        for func in funcs:
            data['result'] = data_recursive(result=data['result'], fn=func)

        return data
