from processor import handler

CATEGORY_BUY_ORDERS = 0
CATEGORY_SELL_ORDERS = 1
CATEGORY_CRYPTO_TYPES = 4
CATEGORY_ISSUANCE = 5
CATEGORY_OWNERS = 6
CATEGORY_BONDS = 7
CATEGORY_BANK_BONDS = 13
CATEGORY_TRADER_BONDS = 8
CATEGORY_TRADER_CRYPTOS = 9
CATEGORY_ORDERS = 10
CATEGORY_CLEARERS = 11
CATEGORY_OWNER_CRYPTO_PUBKEYS = 12

ADDRESS_LEGNTH = 70

def get_category_prefix(category):
    # We need to zero pad so that (for example) '4' becomes '04'
    return 'b04d' + ('0' + hex(category)[2:])[-2:]

def add_category(category):
    def decorator(method):
        def category_adder(*args, **kwargs):
            return get_category_prefix(category) + method(*args, **kwargs)
        return category_adder
    return decorator

def zero_pad(method):
    global ADDRESS_LEGNTH
    def padder(*args, **kwargs):
        address = method(*args, **kwargs)
        return '0' * (ADDRESS_LEGNTH - 6 - len(address)) + address
    return padder

def prefixify(category):
    def decorator(method):
        @add_category(category)
        @zero_pad
        def prefixer(*args, **kwargs):
            return method(*args, **kwargs)
        return prefixer
    return decorator

@prefixify(CATEGORY_BUY_ORDERS)
def get_buy_order_address(buy_asset_type_uuid, sell_asset_type_uuid):
    return buy_asset_type_uuid + sell_asset_type_uuid

@prefixify(CATEGORY_SELL_ORDERS)
def get_sell_order_address(sell_asset_type_uuid, buy_asset_type_uuid):
    return sell_asset_type_uuid + buy_asset_type_uuid

@prefixify(CATEGORY_ISSUANCE)
def get_issuance_address(issuance_uuid):
    return issuance_uuid

@prefixify(CATEGORY_BONDS)
def get_bond_address(bond_uuid):
    return bond_uuid

@prefixify(CATEGORY_OWNERS)
def get_owner_address(owner_pubkey):
    return owner_pubkey[:32]

@prefixify(CATEGORY_BANK_BONDS)
def get_bank_bonds_address(bank_pubkey, issuance_uuid):
    return bank_pubkey[:32] + issuance_uuid

@prefixify(CATEGORY_TRADER_BONDS)
def get_trader_bonds_address(trader_pubkey, issuance_uuid):
    return trader_pubkey[:32] + issuance_uuid

@prefixify(CATEGORY_TRADER_CRYPTOS)
def get_trader_cryptos_address(trader_pubkey, crypto_type_uuid):
    return trader_pubkey[:32] + crypto_type_uuid

@prefixify(CATEGORY_CRYPTO_TYPES)
def get_crypto_type_address(crypto_type_uuid):
    return crypto_type_uuid

@prefixify(CATEGORY_ORDERS)
def get_order_address(order_uuid):
    return order_uuid

@prefixify(CATEGORY_CLEARERS)
def get_clearer_address(clearer_pubkey):
    return clearer_pubkey[:32]

@prefixify(CATEGORY_OWNER_CRYPTO_PUBKEYS)
def get_owner_crypto_pubkeys_address(owner_pubkey, crypto_type_uuid):
    return owner_pubkey[:32] + crypto_type_uuid
