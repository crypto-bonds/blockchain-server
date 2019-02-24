import json

from processor import get_addresses

def get_buy_order_data(buy_asset_type_uuid, sell_asset_type_uuid):
    address = get_addresses.get_buy_order_address(buy_asset_type_uuid, sell_asset_type_uuid)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_sell_order_data(sell_asset_type_uuid, buy_asset_type_uuid):
    address = get_addresses.get_sell_order_address(sell_asset_type_uuid, buy_asset_type_uuid)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_issuance_data(issuance_uuid):
    address = get_addresses.get_issuance_address(issuance_uuid)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_bond_data(bond_uuid):
    address = get_addresses.get_bond_address(bond_uuid)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_owner_data(owner_pubkey):
    address = get_addresses.get_owner_address(owner_pubkey)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_bank_bonds_data(bank_pubkey, issuance_uuid):
    address = get_addresses.get_bank_bonds_address(bank_pubkey, issuance_uuid)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_trader_bonds_data(trader_pubkey, issuance_uuid):
    address = get_addresses.get_trader_bonds_address(trader_pubkey, issuance_uuid)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_trader_cryptos_data(trader_pubkey, crypto_type_uuid):
    address = get_addresses.get_trader_cryptos_address(trader_pubkey, crypto_type_uuid)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_crypto_type_data(crypto_type_uuid):
    address = get_addresses.get_crypto_type_address(crypto_type_uuid)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_order_data(order_uuid):
    address = get_addresses.get_order_address(order_uuid)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_clearer_data(clearer_pubkey):
    address = get_addresses.get_clearer_address(clearer_pubkey)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_owner_crypto_pubkeys_data(owner_pubkey, crypto_type_uuid):
    address = get_addresses.get_owner_crypto_pubkeys_address(owner_pubkey, crypto_type_uuid)
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)