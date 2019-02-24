import json

from processor import get_addresses

def query(context, address):
    data = context.get_state([address])[address]
    if data is None:
        return None
    return json.loads(data)

def get_buy_order_data(context, buy_asset_type_uuid, sell_asset_type_uuid):
    address = get_addresses.get_buy_order_address(buy_asset_type_uuid, sell_asset_type_uuid)
    return query(context, address)

def get_sell_order_data(context, sell_asset_type_uuid, buy_asset_type_uuid):
    address = get_addresses.get_sell_order_address(sell_asset_type_uuid, buy_asset_type_uuid)
    return query(context, address)

def get_issuance_data(context, issuance_uuid):
    address = get_addresses.get_issuance_address(issuance_uuid)
    return query(context, address)

def get_bond_data(context, bond_uuid):
    address = get_addresses.get_bond_address(bond_uuid)
    return query(context, address)

def get_owner_data(context, owner_pubkey):
    address = get_addresses.get_owner_address(owner_pubkey)
    return query(context, address)

def get_bank_bonds_data(context, bank_pubkey, issuance_uuid):
    address = get_addresses.get_bank_bonds_address(bank_pubkey, issuance_uuid)
    return query(context, address)

def get_trader_bonds_data(context, trader_pubkey, issuance_uuid):
    address = get_addresses.get_trader_bonds_address(trader_pubkey, issuance_uuid)
    return query(context, address)

def get_trader_cryptos_data(context, trader_pubkey, crypto_type_uuid):
    address = get_addresses.get_trader_cryptos_address(trader_pubkey, crypto_type_uuid)
    return query(context, address)

def get_crypto_type_data(context, crypto_type_uuid):
    address = get_addresses.get_crypto_type_address(crypto_type_uuid)
    return query(context, address)

def get_order_data(context, order_uuid):
    address = get_addresses.get_order_address(order_uuid)
    return query(context, address)

def get_clearer_data(context, clearer_pubkey):
    address = get_addresses.get_clearer_address(clearer_pubkey)
    return query(context, address)

def get_owner_crypto_pubkeys_data(context, owner_pubkey, crypto_type_uuid):
    address = get_addresses.get_owner_crypto_pubkeys_address(owner_pubkey, crypto_type_uuid)
    return query(context, address)