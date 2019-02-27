from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction

import json

from processor.actions import issue_bonds, buy_bonds_otc, initiate_trade, cancel_trade, accept_trade, add_crypto_type, add_crypto, add_clearer, add_bank, add_trader

class BondHandler(TransactionHandler):
    @property
    def family_name(self):
        return 'crypto-bonds'

    @property
    def family_versions(self):
        return ['0.0']

    @property
    def namespaces(self):
        return ['b04d']  # Thanks @Zac Delventhal

    def apply(self, txn, context):
        try:
            print('Received transaction')
            payload_dict = json.loads(txn.payload.decode('utf-8'))
            method_name = payload_dict['method_name']
            message_dict = payload_dict['message_dict']
        except Exception as e:
            print("Exception encountered in initial transaction processing. Request must be a JSON dict with keys 'method_name' and 'message_dict'")
            raise InvalidTransaction(e)

        methods = {
            'issue_bonds': issue_bonds,
            'buy_bonds_otc': buy_bonds_otc,
            'initiate_trade': initiate_trade,
            'cancel_trade': cancel_trade,
            'accept_trade': accept_trade,
            'add_crypto_type': add_crypto_type,
            'add_crypto': add_crypto,
            'add_clearer': add_clearer,
            'add_bank': add_bank,
            'add_trader': add_trader
        }

        try:
            print(txn)
            print(type(txn.header))
            methods[method_name](context, txn.header.signer_public_key, message_dict)
            print('Processed Transaction!!!')
        except KeyError as e:
            print('Method does not exist')
            raise InvalidTransaction(e)
        except Exception as e:
            print(e)
            print('An error occurred when trying to execute transaction')
            raise InvalidTransaction(e)
