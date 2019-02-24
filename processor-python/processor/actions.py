from uuid import uuid4
import json

from processor import get_addresses


def is_clearer(context, initiator_pubkey):
    clearer_addr = get_addresses.get_clearer_address(initiator_pubkey)
    state_info = context.get_state([clearer_addr])
    if state_info[clearer_addr] is None:
        return False
    return True

def is_bank(context, bank_pubkey):
    bank_address = get_owner_address(bank_pubkey)
    bank_state_info = context.get_state([bank_address])
    if bank_info[bank_address] is None:
        return False
    else:
        bank_data = json.loads(bank_info[bank_address].decode('utf-8'))
        if bank_data['type'] != 'bank':
            return False
    return True

def is_trader(context, trader_pubkey):
    trader_address = get_owner_address(trader_pubkey)
    trader_state_info = context.get_state([trader_address])
    if trader_info[trader_address] is None:
        return False
    else:
        trader_data = json.loads(trader_info[trader_address].decode('utf-8'))
        if trader_data['type'] != 'trader':
            return False
    return True

def issue_bond(context, initiator_pubkey, message_dict):

    if not is_bank(context, message_dict['bank_pubkey'])
        return
    if not is_clearer(context, initiator_pubkey):
        return

    new_state_dict = {}
        
    # create bond type
    issuance_address = get_addresses.get_issuance_address(message_dict['issuance_uuid'])
    issuance_data = {
        'company_pubkey': message_dict['company_pubkey'],
        'bank_pubkey': message_dict['bank_pubkey'],
        'num_issued': message_dict['num_issued'],
        'denomination': message_dict['denomination'],
        'interest_rate': message_dict['interest_rate'],
        'maturity_date': message_dict['maturity_date']
    }

    issuance_data['serials'] = sorted([
                uuid4().hex for _ in range(message_dict['num_issued'])
            ])
            
    new_state_dict[issuance_address] = json.dumps(issuance_data, sort_keys=True)

    # create bonds
    for bond_uuid in issuance_data['serials']:
        new_state_dict[get_issuance_address(bond_uuid)] = {
                'owner_uuid': message_dict['bank_uuid'],
                'issuance_uuid': bond_uuid
        }

    # assign bonds to owner
    bank_bonds_address = get_addresses.get_bank_bonds_address(message_dict['bank_pubkey'], message_dict['issuance_uuid'])
    new_state_dict[bank_bonds_address] = {
        'num_owned': len(issuance_data['serials']),
        'serials': issuance_data['serials']
    }

    context.set_state(new_state_dict)

def buy_bonds_otc(context, initiator_pubkey, message_dict):
    # transfer bonds from bank to trader
    # make sure bank is bank
    # make sure trader is trader

    if not is_clearer(initiator_pubkey):
        return
    if not is_bank(message_dict['bank_pubkey']):
        return
    if not is_trader(message_dict['trader_pubkey']):
        return
    
    # get the first ids from the bank
    message_dict['issuance_uuid']
    num_bought = message_dict['num_bought']

    bonds_address = get_addresses.get_bank_bonds_address(message_dict['bank_pubkey'], message_dict['issuance_uuid'])
    bonds_to_transfer = 


    # change owner on bonds
    # change totals and serials for bank (bank bonds)
    # change totals and serials for trader (trader bonds)
    # change bank bonds
    context.set_state(new_state_dict)

def initiate_trade(context, initiator_pubkey, message_dict):
    pass

def cancel_trade(context, initiator_pubkey, message_dict):
    pass

def accept_trade(context, initiator_pubkey, message_dict):
    pass

def add_crypto(context, initiator_pubkey, message_dict):
    pass
