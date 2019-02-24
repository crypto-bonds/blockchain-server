from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction

import json

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
            payload_dict = json.loads(txn.payload.decode('utf-8'))
            method_name = payload_dict['method_name']
            parameter_dict = payload_dict['method_dict']
        except Exception as e:
            raise InvalidTransaction(e)

        methods = {
            'issue_bonds': issue_bonds,
            'buy_bonds_otc': buy_bonds_otc,
            'initiate_trade': initiate_trade,
            'cancel_trade': cancel_trade,
            'accept_trade': accept_trade,
            'add_crypto': add_crypto
        }

        methods[method_name](context, initiator_pubkey, parameter_dict)
