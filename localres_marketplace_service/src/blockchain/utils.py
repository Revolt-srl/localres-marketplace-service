from algosdk import account, encoding, transaction
from algosdk.mnemonic import to_private_key
from pydantic import BaseModel


class TransactionInfo(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    tx_id: str
    confirmed_round: int
    tx_info: dict


def extract_ps_values(ps_value: str):
    """
    Extracts the values for 'ps_' from the string parameter.

    :param ps_value: The string with the values inside.
    :return: A list with the extracted values.
    """
    ps_values = []
    for i in range(0, len(ps_value), 3):
        ps_values.append(ps_value[i:i + 3])
    return ps_values


def extract_values(data_bytes: bytes):
    """
    Extracts the value for 'balance_' and 'ps_' from the byte string parameter.

    :param data_bytes: The byte string with data inside.
    :return: A dictionary with the extraced values.
    """
    ps_index = data_bytes.find(b"ps_")
    balance_index = data_bytes.find(b"balance_")

    
    ps_value = data_bytes[ps_index:balance_index] if ps_index != - \
        1 and balance_index != -1 else None
    balance_value = data_bytes[balance_index:] if balance_index != -1 else None

    if ps_value:
        ps_value = ps_value.split(b"ps_")[1]
        ps_value = ps_value.decode('utf-8')
        ps_value = extract_ps_values(ps_value)
    if balance_value:
        balance_value = balance_value.split(b"balance_")[1]
        balance_value = int.from_bytes(balance_value, 'big')

    return balance_value, ps_value


def wait_for_confirmation(client, tx_id) -> TransactionInfo:
    """
    Utility function that waits for a transaction to be confirmed on the blockchain.
    """
    last_round = client.status().get("last-round")
    tx_info = client.pending_transaction_info(tx_id)
    while not (tx_info.get("confirmed-round") and tx_info.get("confirmed-round") > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        tx_info = client.pending_transaction_info(tx_id)
    print(
        "Transaction {} confirmed in round {}.".format(
            tx_id, tx_info.get("confirmed-round")
        )
    )
    return TransactionInfo(tx_id=tx_id, confirmed_round=tx_info["confirmed-round"], tx_info=tx_info)


def change_owner(algod_client, mnemonic_phrase, app_id, new_owner):
    sender = account.address_from_private_key(to_private_key(mnemonic_phrase))
    params = algod_client.suggested_params()

    params.flat_fee = True
    params.fee = 1000

    txn = transaction.ApplicationNoOpTxn(
        sender=sender,
        sp=params,
        index=app_id,
        app_args=[b"change_owner"],
        accounts=[new_owner]
    )

    signed_txn = txn.sign(to_private_key(mnemonic_phrase))
    tx_id = signed_txn.transaction.get_txid()

    algod_client.send_transactions([signed_txn])
    wait_for_confirmation(algod_client, tx_id)


def address_to_bytes(address: str) -> bytes:
    """
    Convert Algorand address to bytes.

    :param address: The Algorand address to convert.

    :return: the bytes representation of the address.
    """
    return encoding.decode_address(address)


def bytes_to_address(address_bytes: bytes) -> str:
    """
    Converts bytes to an Algorand address.

    :param address_bytes: the bytes to convert.
    :return: the Algorand address as a string.
    """
    return encoding.encode_address(address_bytes)
