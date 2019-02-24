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
    for serial in issuance_data['serials']:
        new_state_dict[get_issuance_address(serial)] = {
                'owner_pubkey': message_dict['bank_pubkey'],
                'issuance_uuid': message_dict['issuance_uuid']
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

    serials_to_transfer = data['serials'][:num_bought]
    serials_to_stay = data['serials'][num_bought:]

    bank_data['num_owned'] -= num_bought
    bank_data['serials'] = serials_to_stay
    new_state_dict[bank_address] = bank_data

    for serial in serials_to_transfer:
        bond_address = get_addresses.get_bond_address(serial)
        bond_data = get_data.query(bond_address)
        bond_data['owner_pubkey'] = message_dict['trader_pubkey']
        new_state_dict[bond_address] = bond_data
    
    trader_address = get_addresses.get_trader_bonds_address(message_dict['trader_pubkey'], message_dict['issuance_uuid'])
    trader_data = get_data.query(trader_address)
    trader_data['total_owned'] += num_bought
    trader_data['serials'] = sorted(trader_data['serials'] + serials_to_transfer)
    new_state_dict[trader_address] = trader_data
    
    context.set_state(new_state_dict)

def initiate_trade(context, initiator_pubkey, message_dict):
    if not is_trader(initiator_pubkey):
        return
    
    order_address = get_addresses.get_order_address(message_dict['order_uuid'])

    if get_data.query(order_address) is not None:
        return  # A new order can't already exist

    trader_address = get_addresses.get_trader_bonds_address(initiator_pubkey, message_dict['sell_asset'])
    trader_data = get_data.query(trader_address)
    if trader_data is None:
        return # None owned
    
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
    buy_address = get_addresses.get_buy_order_address(message_dict['buy_asset_type'], message_dict['sell_asset_type'])
    sell_address = get_addresses.get_sell_order_address(message_dict['sell_asset_type'], message_dict['buy_asset_type'])
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
    # in this context, there is initiator_pubkey and order_data['initiator_pubkey']
    # initiator_pubkey initiates the acceptance
    # order_data['initiator_pubkey'] initiated the order

    if not is_trader(initiator_pubkey):
        return
    
    order_address = get_addresses.get_order_address(message_dict['order_uuid'])
    order_data = get_data.query(order_address)

    # Call it bond because in the future, we also want to use crypto and distinguish between the two
    trade_initiator_bond_asset1_address = get_addresses.get_trader_bonds_address(order_data['initiator_pubkey'], order_data['sell_asset_type'])
    trade_initiator_bond_asset2_address = get_addresses.get_trader_bonds_address(order_data['initiator_pubkey'], order_data['buy_asset_type'])

    trade_acceptor_bond_asset1_address = get_addresses.get_trader_bonds_address(initiator_pubkey, order_data['sell_asset_type'])
    trade_acceptor_bond_asset2_address = get_addresses.get_trader_bonds_address(initiator_pubkey, order_data['buy_asset_type'])

    # asset 1 goes from initiator to acceptor
    # asset 2 goes from acceptor to initiator
    trade_acceptor_bond_asset2_data = get_data.query(trade_acceptor_bond_asset2_address)
    if trade_acceptor_bond_asset2_data is None:
        return  # Trader has none
    
    if trade_acceptor_bond_asset2_data['total_owned'] - trade_acceptor_bond_asset2_data['num_in_orders'] < order_data['num_to_buy']:
        return  # Not enough to fulfill

    # remove order from order books
    buy_order_address = get_addresses.get_buy_order_address(order_data['sell_asset_type'], order_data['buy_asset_type'])
    sell_order_address = get_addresses.get_sell_order_address(order_data['buy_asset_type'], order_data['sell_asset_type'])
    buy_order_data = get_data.query(buy_order_address)
    sell_order_data = get_data.query(sell_order_address)

    buy_order_data['orders'].remove(message_dict['order_uuid'])
    sell_order_data['orders'].remove(message_dict['order_uuid'])

    # save updated order books
    new_state_dict[buy_order_address] = buy_order_data
    new_state_dict[sell_order_address] = sell_order_data
    
    # start manipulaing trader data
    trade_initiator_bond_asset1_data = get_data.query(trade_initiator_bond_asset1_address)
    trade_initiator_bond_asset2_data = get_data.query(trade_initiator_bond_asset2_address)
    
    trade_acceptor_bond_asset1_data = get_data.query(trade_acceptor_bond_asset1_address)
    trade_acceptor_bond_asset2_data = get_data.query(trade_acceptor_bond_asset2_address)

    if trade_initiator_bond_asset2_data is None:
        trade_initiator_bond_asset2_data = {
            'total_owned': 0,
            'num_in_orders': 0,
            'serials': [],
            'orders': []
        }
    
    if trade_acceptor_bond_asset1_data is None:
        trade_acceptor_bond_asset1_data = {
            'total_owned': 0,
            'num_in_orders': 0,
            'serials': [],
            'orders': []
        }

    # remove order from initiator order list
    trade_initiator_bond_asset1_data['orders'].remove(message_dict['order_uuid'])

    # delete order
    new_state_dict[order_address] = None  # TODO This may not be right

    # move asset 1
    asset1_serials_to_move = trade_initiator_bond_asset1_data['serials'][:order_data['num_to_sell']]
    asset1_serials_to_stay = trade_initiator_bond_asset1_data['serials'][order_data['num_to_sell']:]

    trade_initiator_bond_asset1_data['num_in_orders'] -= order_data['num_to_sell']
    trade_initiator_bond_asset1_data['total_owned'] -= order_data['num_to_sell']
    trade_initiator_bond_asset1_data['serials'] = asset1_serials_to_stay

    trade_acceptor_bond_asset1_data['total_owned'] += order_data['num_to_sell']
    trade_acceptor_bond_asset1_data['serials'] = sorted(trade_acceptor_bond_asset1_data['serials'] + asset1_serials_to_move)
    
    # move asset 2
    asset2_serials_to_move = trade_acceptor_bond_asset2_data['serials'][:order_data['num_to_buy']]
    asset2_serials_to_stay = trade_acceptor_bond_asset2_data['serials'][order_data['num_to_buy']:]

    # skip num_in_orders because acceptor never places order
    trade_acceptor_bond_asset2_data['total_owned'] -= order_data['num_to_buy']
    trade_acceptor_bond_asset2_data['serials'] = asset2_serials_to_stay

    trade_initiator_bond_asset2_data['total_owned'] += order_data['num_to_buy']
    trade_initiator_bond_asset2_data['serials'] = sorted(trade_acceptor_bond_asset2_data['serials'] + asset2_serials_to_move)

    # commit asset movements
    new_state_dict[trade_initiator_bond_asset1_address] = trade_initiator_bond_asset1_data
    new_state_dict[trade_initiator_bond_asset2_address] = trade_initiator_bond_asset2_data

    new_state_dict[trade_acceptor_bond_asset1_address] = trade_acceptor_bond_asset1_data
    new_state_dict[trade_acceptor_bond_asset2_address] = trade_acceptor_bond_asset2_data

    # reassign individual bonds
    for serial in asset1_serials_to_move:
        bond_address = get_addresses.get_bond_address(serial)
        bond_data = get_data.query(bond_address)
        bond_data['owner_pubkey'] = initiator_pubkey
        new_state_dict[bond_address] = bond_data
    
    for serial in asset2_serials_to_move:
        bond_address = get_addresses.get_bond_address(serial)
        bond_data = get_data.query(bond_address)
        bond_data['owner_pubkey'] = order_data['initiator_pubkey']
        new_state_dict[bond_address] = bond_data

    context.set_state(new_state_dict)

def add_crypto(context, initiator_pubkey, message_dict):
    pass

def add_clearer(context, initiator_pubkey, message_dict):
    pass

def add_bank(context, initiator_pubkey, message_dict):
    pass

def add_trader(context, initiator_pubkey, message_dict):
    pass
