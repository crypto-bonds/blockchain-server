from uuid import uuid4
import json

from processor import get_addresses, get_data


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
                'owner_pubkey': message_dict['bank_pubkey'],
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
    
    new_state_dict = {}

    # get the first ids from the bank
    num_bought = message_dict['num_bought']

    bank_address = get_addresses.get_bank_bonds_address(message_dict['bank_pubkey'], message_dict['issuance_uuid'])
    bank_data = get_data.query(bank_address)
    if num_bought > num_owned:
        return  # transaction failed

    bonds_to_transfer = data['serials'][:num_bought]
    bonds_to_stay = data['serials'][num_bought:]

    bank_data['num_owned'] -= num_bought
    bank_data['serials'] = bonds_to_stay
    new_state_dict[bank_address] = bank_data

    for bond_uuid in bonds_to_transfer:
        bond_address = get_addresses.get_bond_address(bond_uuid)
        bond_data = get_data.query(bond_address)
        bond_data['owner_pubkey'] = message_dict['trader_pubkey']
        new_state_dict[bond_address] = bond_data
    
    trader_address = get_addresses.get_trader_bonds_address(message_dict['trader_pubkey'], message_dict['issuance_uuid'])
    trader_data = get_data.query(trader_address)
    trader_data['total_owned'] += num_bought
    trader_data['serials'] = sorted(trader_data['serials'] + bonds_to_transfer)
    new_state_dict[trader_address] = trader_data
    
    context.set_state(new_state_dict)

def initiate_trade(context, initiator_pubkey, message_dict):
    if not is_trader(initiator_pubkey):
        return
    
    order_address = get_addresses.get_order_address(message_dict['order_uuid'])

    if get_data.query(order_address) is not None:
        return  # A new order can't already exist

    trader_address = get_addresses.get_trader_bonds_address(initiator_pubkey)
    trader_data = get_data.query(trader_address)
    
    if trader_data['total_owned'] - trader_data['num_in_orders'] < message_dict['num_to_sell']:
        return  # Can only sell ones that are not already in orders

    new_state_dict = {}

    # Creates order
    new_state_dict[order_address] = {
        'initiator_pubkey' = initiator_pubkey,
        'sell_asset_type' = message_dict['sell_asset_type'],
        'buy_asset_type' = message_dict['buy_asset_type'],
        'num_to_sell' = message_dict['num_to_sell'],
        'num_to_buy' = message_dict['num_to_buy']
    }

    # Update trader's totals
    trader_data['num_in_orders'] += trader_data['num_to_sell']
    trader_data['orders'] = sorted(trader_data['orders'] + [message_dict['order_uuid']])
    
    new_state_dict[trader_address] = trader_data

    # Keep track of the orderbook
    # Buy + sell is redundant, but good for indexing. Buying one bond for $1 is the same as selling $1 for one bond
    buy_address = get_addresses.get_buy_address(message_dict['buy_asset_type'], message_dict['sell_asset_type'])
    sell_address = get_addresses.get_sell_address(message_dict['sell_asset_type'], message_dict['buy_asset_type'])
    buy_data = get_data.query(buy_address)
    sell_data = get_data.query(sell_address)
    buy_data['orders'] = sorted(buy_data['orders'] + [message_dict['order_uuid']])
    sell_data['orders'] = buy_data['orders']
    new_state_dict[buy_address] = buy_data
    new_state_dict[sell_data] = sell_data

    context.set_state(new_state_dict)

def cancel_trade(context, initiator_pubkey, message_dict):
    pass

def accept_trade(context, initiator_pubkey, message_dict):
    pass

def add_crypto(context, initiator_pubkey, message_dict):
    pass

def add_clearer(context, initiator_pubkey, message_dict):   
    clearer_address =  get_addresses.get_clearer_address(initiator_pubkey):
    clearer_data = {
        'pubkey': clearer_address
    }
    new_state_dict = {
        clearer_address: clearer_data
    }
    context.set_state(new_state_dict)

    

def add_bank(context, initiator_pubkey, message_dict):   
    bank_address = get_addresses.get_owner_address(initiator_pubkey):
    bank_data = {
        'pubkey':bank_address
    }
    new_state_dict = {
        bank_address: bank_data
    }
    context.set_state(new_state_dict)

def add_trader(context, initiator_pubkey, message_dict):
    trader_address = get_addresses.get_owner_address(initiator_pubkey):
    trader_data = {
        'pubkey':trader_address
    }
    new_state_dict = {
        trader_address: trader_data
    }
    context.set_state(new_state_dict)
