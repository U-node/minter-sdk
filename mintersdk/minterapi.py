'''
Created on 26 окт. 2018 г.

@author: Roman
'''
import requests
import json
from http.client import HTTPException


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
    
    def __init__(self, api_url, **kwargs):
        """
        @param api_url|string: API host, e.g. http://localhost/api/
        @param kwargs: available attributes are
            - connect_timeout|float,int
            - read_timeout|float|int
        """
        self.api_url = api_url
        
        for name, value in kwargs.items():
            setattr(self, name, value)
        
    def __setattr__(self, name, value):
        if not hasattr(self, name):
            raise KeyError('Attribute {} is not available for this class'.format(name))
        
        return super.__setattr__(self, name, value)
    
    def get_balance(self, address, height=None):
        """
        Get balance by address
            @param address|string: wallet address
            @param height|int: block height
        """
        return self._request('address', params={'address': address, 'height': height})
    
    def get_nonce(self, address):
        """
        Nonce - int, used for prevent transaction reply
            @param address|string: wallet address
        """
        
        return int(self.get_balance(address)['result']['transaction_count']) + 1
    
    def get_status(self):
        """
        Get node status
        """
        return self._request('status')
        
    def get_candidate(self, public_key, height=None):
        """
        Get canditate
            @param public_key|string: candidate public key
            @param height|int: block height
        """
        return self._request('candidate', params={'pubkey': public_key, 'height': height})
            
    def get_candidates(self, height=None):
        """
        Get candidates
            @param height|int: block height
        """
        return self._request('candidates', params={'height': height})
      
    def get_validators(self, height=None):
        """
        Get validators list
            @param height|int: get validators on specified block height 
        """
            
        return self._request('validators', params={'height': height})
    
    def estimate_coin_buy(self, coin_to_sell, value_to_buy, coin_to_buy, height=None):
        """
        Return estimate of buy coin transaction
            @param coin_to_sell|string: coin name to sell
            @param value_to_buy|string: amount of coins to buy
            @param coin_to_buy|string: coin name to buy
            @param height|int: block height
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
        
    def estimate_coin_sell(self, coin_to_sell, value_to_sell, coin_to_buy, height=None):
        """
        Return estimate of sell coin transaction
            @param coin_to_sell|string: coin name to sell
            @param value_to_sell|string: amount of coins to sell
            @param coin_to_buy|string: coin name to buy
            @param height|int: block height
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
        
    def get_coin_info(self, symbol, height=None):
        """
        Get information about coin
            @param symbol|string: coin name
            @param height|int: block height
        """
        return self._request('coin_info', params={'symbol': symbol, 'height': height})
    
    def get_block(self, height):
        """
        Get block data at given height
            @param height|int: block height 
        """
        return self._request('block', params={'height': height})
    
    def get_transaction(self, tx_hash):
        """
        Get transaction info
            @param hash|string: transaction hash 
        """
        return self._request('transaction', params={'hash': tx_hash})
    
    def send_transaction(self, tx):
        """
        Send transaction
            @param tx|string: signed transaction to send 
        """

        return self._request('send_transaction', params={'tx': '0x' + tx})
    
    def _request(self, command, request_type='get', **kwargs):
        """
        Send all requests to API
        """
        # Add timeouts if were not set
        if not kwargs.get('timeout', None):
            kwargs['timeout'] = (self.connect_timeout, self.read_timeout)
        
        # Trying make request    
        try:
            url = self.api_url + command
            
            if request_type == 'get':
                response = requests.get(url, **kwargs)
            elif request_type == 'post':
                response = requests.post(url, **kwargs)
            
            # If everything is ok, API return 200 with response data in json
            if response.ok:
                return response.json() 
            
            # It response is not ok
            raise HTTPException('HTTP error (code: {})'.format(response.status_code))
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