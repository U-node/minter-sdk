<p align="center" background="black"><img src="un_top.svg" width="450"></p>

<p align="center">
</p>

Python SDK

Ported from official Minter's <a href="https://github.com/MinterTeam/minter-php-sdk">php SDK</a>

Created by <a href="https://www.u-node.net">https://www.u-node.net</a>'s masternode co-founder Roman Matusevich 

You can support our project by sending any Minter's coins to our wallet Mx6e0cd64694b1e143adaa7d4914080e748837aec9

Feel free to delegate to our 3% masternode Mp02bc3c3f77d5ab9732ef9fc3801a6d72dc18f88328c14dc735648abfe551f50f


## SDK use

You can create transaction by import transaction class and create object of this class.

### Create tx

```python
from mintersdk.sdk.transactions import MinterDelegateTx
tx = MinterDelegateTx(pub_key='Mp...', coin='MNT', stake=1, nonce=1, gas_coin='MNT')
```

### Sign tx

``
tx.sign('PRIVATE_KEY')
``

### You can get signed_tx from signed_tx attribute

``
tx.signed_tx
``

To get all required and optional arguments, look for source code.

### To create tx object from raw tx

```python
from mintersdk.sdk.transactions import MinterTx
tx = MinterTx.from_raw(raw_tx='...')
```

You will get tx object of tx type.
