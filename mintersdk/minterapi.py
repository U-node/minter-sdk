'''
Created on 26 окт. 2018 г.

@author: Roman
'''
import requests


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
        @param api_url|string: API host, e.g. http://localhost/api/
        @param kwargs: available attributes are
            - connect_timeout|float,int
            - read_timeout|float|int
            - req_headers|object
        """
        self.api_url = api_url
        if self.api_url[-1] != '/':
            self.api_url += '/'

        for name, value in kwargs.items():
            setattr(self, name, value)

    def __setattr__(self, name, value):
        if not hasattr(self, name):
            raise KeyError('Attribute {} is not available for this class'.format(name))

        return super.__setattr__(self, name, value)

    def get_status(self):
        """
        Get node status
        """
        return self._request('status')

    def get_candidate(self, public_key, height=None):
        """
        Get canditate
        Args:
            public_key (string): candidate public key
            height (int): block height
        """
        return self._request('candidate',
                             params={'pub_key': public_key, 'height': height})

    def get_validators(self, height=None):
        """
        Get validators list
        Args:
            height (int): get validators on specified block height
        """
        return self._request('validators', params={'height': height})

    def get_balance(self, address, height=None):
        """
        Get balance by address
        Args:
            address (string): wallet address
            height (int): block height
        """
        return self._request('address',
                             params={'address': address, 'height': height})

    def get_nonce(self, address):
        """
        Nonce - int, used for prevent transaction reply
        Args:
            address (string): wallet address
        """

        balance = self.get_balance(address)
        nonce = int(balance['result']['transaction_count']) + 1

        return nonce

    def send_transaction(self, tx):
        """
        Send transaction
        Args:
            tx (string): signed transaction to send
        """
        return self._request('send_transaction', params={'tx': '0x' + tx})

    def get_transaction(self, tx_hash):
        """
        Get transaction info
        Args:
            hash (string): transaction hash
        """
        tx_hash = '0x' + tx_hash

        return self._request('transaction', params={'hash': tx_hash})

    def get_block(self, height):
        """
        Get block data at given height
        Args:
            height (int): block height
        """
        return self._request('block', params={'height': height})

    def get_events(self, height):
        """
        Get events at given height
        Args:
            height (int): block height
        """
        return self._request('events', params={'height': height})

    def get_candidates(self, height=None, include_stakes=False):
        """
        Get candidates
        Args:
            height (int): block height
        """
        return self._request(
            'candidates',
            params={
                'height': height,
                'include_stakes': str(include_stakes).lower()
            }
        )

    def get_coin_info(self, symbol, height=None):
        """
        Get information about coin
        Args:
            symbol (string): coin name
            height (int): block height
        """
        return self._request('coin_info',
                             params={'symbol': symbol, 'height': height})

    def estimate_coin_sell(self, coin_to_sell, value_to_sell,
                           coin_to_buy, height=None):
        """
        Return estimate of sell coin transaction
        Args:
            coin_to_sell (string): coin name to sell
            value_to_sell (string): amount of coins to sell
            coin_to_buy (string): coin name to buy
            height (int): block height
        """
        return self._request(
            'estimate_coin_sell',
            params={
                'coin_to_sell': coin_to_sell,
                'value_to_sell': value_to_sell,
                'coin_to_buy': coin_to_buy,
                'height': height
            }
        )

    def estimate_coin_buy(self, coin_to_sell, value_to_buy,
                          coin_to_buy, height=None):
        """
        Return estimate of buy coin transaction
        Args:
            coin_to_sell (string): coin name to sell
            value_to_buy (string): amount of coins to buy
            coin_to_buy (string): coin name to buy
            height (int): block height
        """
        return self._request(
            'estimate_coin_buy',
            params={
                'coin_to_sell': coin_to_sell,
                'value_to_buy': value_to_buy,
                'coin_to_buy': coin_to_buy,
                'height': height
            }
        )

    def estimate_tx_comission(self, tx):
        """
        Estimate current tx gas.
        Args:
            tx (string): signed transaction
        """
        if tx[:2] != '0x':
            tx = '0x' + tx

        return self._request('estimate_tx_commission', params={'tx': tx})

    def get_transactions(self, query, page=None, limit=None):
        """
        Get transactions by query.
        Args:
            query (string)
            page (int)
            limit (int)
        """
        return self._request('transactions', params={'query': query, 'page': page, 'perPage': limit})

    def get_unconfirmed_transactions(self, limit=None):
        """
        Get unconfirmed transactions.
        Args:
            limit (int)
        """
        return self._request('unconfirmed_txs', params={'limit': limit})

    def get_max_gas_price(self, height=None):
        """
        Returns current max gas price.
        Args:
            height (int)
        """
        return self._request('max_gas', params={'height': height})

    def get_min_gas_price(self):
        """
        Returns min gas price.
        """
        return self._request('min_gas_price')

    def get_missed_blocks(self, public_key, height=None):
        """
        Returns missed blocks by validator public key.
        Args:
            public_key (str): candidate public key
            height (int): block chain height
        """
        return self._request(
            'missed_blocks',
            params={'pub_key': public_key, 'height': height}
        )

    def _request(self, command, request_type='get', **kwargs):
        """
        Send all requests to API
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

            # Try to get json response.
            try:
                return response.json()
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
