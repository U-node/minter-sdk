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
    
    def get_balance(self, address):
        """
        Get balance by address
            @param address|string: wallet address
        """
        return self._request('balance/{}'.format(address))
    
    def get_nonce(self, address):
        """
        Nonce - int, used for prevent transaction reply
            @param address|string: wallet address
        """
        return self._request('transactionCount/{}'.format(address))
    
    def get_status(self):
        """
        Get node status
        """
        return self._request('status')
        
    def get_candidate(self, public_key):
        """
        Get canditate
            @param public_key|string: candidate public key 
        """
        return self._request('candidate/{}'.format(public_key))
            
    def get_candidates(self):
        """
        Get candidates
        """
        return self._request('candidates')
      
    def get_validators(self, height=None):
        """
        Get validators list
            @param height|int: get validators on specified block height  
        """
        command = 'validators'
        params = None
        
        if height:
            params = {'height': height}
            
        return self._request(command, params=params)
    
    def estimate_coin_buy(self, coin_to_sell, value_to_buy, coin_to_buy):
        """
        Return estimate of buy coin transaction
            @param coin_to_sell|string: coin name to sell
            @param value_to_buy|string: amount of coins to buy
            @param coin_to_buy|string: coin name to buy  
        """
        return self._request(
                        'estimateCoinBuy', 
                        params={
                            'coin_to_sell': coin_to_sell,
                            'value_to_buy': value_to_buy,
                            'coin_to_buy': coin_to_buy
                        }
                    )
        
    def estimate_coin_sell(self, coin_to_sell, value_to_sell, coin_to_buy):
        """
        Return estimate of sell coin transaction
            @param coin_to_sell|string: coin name to sell
            @param value_to_sell|string: amount of coins to sell
            @param coin_to_buy|string: coin name to buy  
        """
        return self._request(
                        'estimateCoinSell', 
                        params={
                            'coin_to_sell': coin_to_sell,
                            'value_to_sell': value_to_sell,
                            'coin_to_buy': coin_to_buy
                        }
                    )
        
    def get_coin_info(self, name):
        """
        Get information about coin
            @param name|string: coin name 
        """
        return self._request('coinInfo/{}'.format(name))
    
    def get_base_coin_volume(self, height):
        """
        Get amount of base coin (BIP or MNT) existing in the network. It counts block rewards, 
        premine and relayed rewards.
            @param height|int: block height
        """
        return self._request('bipVolume', params={'height': height})
    
    def get_block(self, height):
        """
        Get block data at given height
            @param height|int: block height 
        """
        return self._request('block/{}'.format(height))
    
    def get_transaction(self, tx_hash):
        """
        Get transaction info
            @param hash|string: transaction hash 
        """
        return self._request('transaction/{}'.format(tx_hash))
    
    def send_transaction(self, tx):
        """
        Send transaction
            @param tx|string: signed transaction to send 
        """

        return self._request('sendTransaction', 
                             request_type='post', 
                             data=json.dumps({'transaction': tx}))
    
    def get_transactions_from(self, address):
        """
        Get outcoming transactions by address
            @param address|string: wallet address without prefix 
        """
        raise NotImplementedError('Method is not implemented yet')
    
    def get_transactions_to(self, address):
        """
        Get incoming transactions by address
            @param address|string: wallet address without prefix 
        """
        raise NotImplementedError('Method is not implemented yet')
    
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
            
            # If request data contains errors, API return 500 status code with error data in json.
            # If everything is ok, API return 200 with response data in json
            if response.status_code in [200, 500]:
                return response.json() 
            # In all other response not ok cases raise error
            elif not response.ok:
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