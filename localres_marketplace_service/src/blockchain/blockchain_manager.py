from localres_marketplace_service.src.blockchain.user import UserViewModel as BlockchainUser
from localres_marketplace_service.src.common.models import GenericUser, TransactionWriteModel
from localres_marketplace_service.src.marketplace.data_types import TradingData
from localres_marketplace_service.src.blockchain.utils import TransactionInfo, extract_values, wait_for_confirmation
from localres_marketplace_service.src.blockchain.user import User, UserViewModel, UserWriteModel
import base64
import os
from typing import Any, Self
from pydantic import BaseModel
from algosdk.v2client import algod, indexer
from algosdk.mnemonic import to_private_key
from algosdk import transaction, account
from option import Err, Ok, Result
import logbook
logg = logbook.Logger(__name__)


class BlockchainManager(BaseModel):
    algod_indexer: indexer.IndexerClient
    algod: algod.AlgodClient
    app_id: int
    mnemonic_phrase: str

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_env(cls) -> Self:
        network = os.environ.get("NETWORK", "testnet").lower()
        if network == "testnet":
            token = os.environ.get("CLIENT_TOKEN")
            address = os.environ.get("CLIENT_API_URL")
            indexer_address = os.environ.get("INDEXER_API_URL")
            mnemonic_phrase = os.environ.get("MNEMONIC_PHRASE")
        elif network == "mainnet":
            token = os.environ.get("MAINNET_CLIENT_TOKEN")
            address = os.environ.get("MAINNET_CLIENT_API_URL")
            indexer_address = os.environ.get("MAINNET_INDEXER_API_URL")
            mnemonic_phrase = os.environ.get("MAINNET_MNEMONIC_PHRASE")
        elif network == "localnet":
            token = os.environ.get("LOCAL_CLIENT_TOKEN")
            address = os.environ.get("LOCAL_CLIENT_API_URL")
            indexer_address = os.environ.get("LOCAL_INDEXER_API_URL")
            mnemonic_phrase = os.environ.get("LOCAL_MNEMONIC_PHRASE")
        else:
            raise ValueError("Invalid network")

        if not token or not address or not indexer_address:
            raise ValueError("Missing environment variables")

        indexer_instance = indexer.IndexerClient(
            indexer_token=token,
            indexer_address=indexer_address,
        )
        client_instance = algod.AlgodClient(
            algod_token=token, algod_address=address)

        app_id = os.environ.get("APP_ID")

        if not app_id:
            raise ValueError("Missing APP_ID environment variable")

        return cls(
            app_id=int(app_id),
            algod_indexer=indexer_instance,
            algod=client_instance,
            mnemonic_phrase=mnemonic_phrase
        )

    def get_user_value(self, user_id) -> Result[list[UserViewModel], Exception]:
        app_info = self.algod_indexer.applications(self.app_id)
        app_global_state = app_info["params"]["global-state"]
        ps_value: list[str] = []
        balance: int = 0
        users: list[UserViewModel] = []
        for state in app_global_state:
            key = base64.b64decode(state["key"]).decode('utf-8')
            if (key == user_id or user_id == "all"):
                raw_value = state["value"]["bytes"]
                balance, ps_value = extract_values(
                    base64.b64decode(raw_value))  # type: ignore
                if balance is not None or ps_value is not None:
                    is_new = all(value == '000' for value in ps_value)
                    if is_new:
                        logg.info(
                            f"the user {user_id} did not set any threshold manually")
                    users.append(
                        User(user_id=key, balance=balance, thresholds=ps_value, is_new=is_new).to_view_model())

        return Ok(users)

    def upsert_user(self, user: UserWriteModel, note: str = "") -> Result[TransactionInfo, Exception]:
        sender = account.address_from_private_key(
            to_private_key(self.mnemonic_phrase))
        params = self.algod.suggested_params()

        params.flat_fee = True
        params.fee = 1000

        txn = transaction.ApplicationNoOpTxn(
            sender=sender,
            sp=params,
            index=self.app_id,
            app_args=[b"update_user", user.user_id, user.user_value],
            note=note
        )
        try:
            signed_txn = txn.sign(to_private_key(self.mnemonic_phrase))
            tx_id = signed_txn.transaction.get_txid()

            self.algod.send_transactions([signed_txn])
            return Ok(wait_for_confirmation(self.algod, tx_id))

        except Exception as e:
            return Err(e)

    def delete_user(self, user_id: str) -> Result[TransactionInfo, Exception]:
        sender = account.address_from_private_key(
            to_private_key(self.mnemonic_phrase))
        params = self.algod.suggested_params()

        params.flat_fee = True
        params.fee = 1000
        txn = transaction.ApplicationNoOpTxn(
            sender=sender,
            sp=params,
            index=self.app_id,
            app_args=[b"delete_user", user_id.encode()],
        )

        signed_txn = txn.sign(to_private_key(self.mnemonic_phrase))
        try:
            tx_id = signed_txn.transaction.get_txid()

            self.algod.send_transactions([signed_txn])

            return Ok(wait_for_confirmation(self.algod, tx_id))
        except Exception as e:
            return Err(e)

    def increment_user_value(self, user_id, balance):
        sender = account.address_from_private_key(
            to_private_key(self.mnemonic_phrase))
        params = self.algod.suggested_params()
        params.flat_fee = True
        params.fee = 1000

        txn = transaction.ApplicationNoOpTxn(
            sender=sender,
            sp=params,
            index=self.app_id,
            app_args=[b"update_user", user_id, balance],
        )

        signed_txn = txn.sign(to_private_key(self.mnemonic_phrase))
        tx_id = signed_txn.transaction.get_txid()

        self.algod.send_transactions([signed_txn])
        wait_for_confirmation(self.algod, tx_id)
        return Err(Exception("User not found"))

    def change_owner(self, new_owner):
        sender = account.address_from_private_key(
            to_private_key(self.mnemonic_phrase))
        params = self.algod.suggested_params()

        params.flat_fee = True
        params.fee = 1000

        txn = transaction.ApplicationNoOpTxn(
            sender=sender,
            sp=params,
            index=self.app_id,
            app_args=[b"change_owner"],
            accounts=[new_owner]
        )

        signed_txn = txn.sign(to_private_key(self.mnemonic_phrase))
        tx_id = signed_txn.transaction.get_txid()

        self.algod.send_transactions([signed_txn])
        wait_for_confirmation(self.algod, tx_id)

    def save_trading_data_to_algorand(self, trading_data: TradingData, keycloack_users: list[GenericUser], blockchain_users: list[BlockchainUser]) -> Result[Any, Exception]:
        try:
            transactions_results: list[TransactionWriteModel] = []
            for consumer_trading_data in trading_data.trading_data:
                for trade in consumer_trading_data["trades"]:
                    logg.info(trade)
                    # Get the consumer
                    keycloack_consumer = [
                        keycloak_user for keycloak_user in keycloack_users if keycloak_user.user_id == consumer_trading_data["id_consumer"]][0]
                    blockchain_consumer = [
                        blockchain_user for blockchain_user in blockchain_users if int(blockchain_user.user_id) == keycloack_consumer.blockchain_id][0]
                    blockchain_consumer.balance += int(trade["given_T"])
                    # Get the producer
                    keycloak_producer = [
                        keycloak_user for keycloak_user in keycloack_users if keycloak_user.user_id == trade["id_prosumer"]][0]
                    blockchain_producer = [
                        blockchain_user for blockchain_user in blockchain_users if int(blockchain_user.user_id) == keycloak_producer.blockchain_id][0]
                    blockchain_producer.balance += int(trade["received_T"])
                    note_given_t = trade["given_T"]
                    note_purchased_energy = trade["purchased_energy"]
                    note_consumer = keycloack_consumer.user_id
                    note_consumer_blockchain_id = blockchain_consumer.user_id
                    note_id_prosumer = trade["id_prosumer"]
                    note_prosumer_given_t = trade["received_T"]
                    str_note = ""
                    if note_purchased_energy == 0:
                        str_note = f"In this transacion the consumer {note_consumer} (Blockchain ID: {note_consumer_blockchain_id}) has not purchased any energy from the producer {note_id_prosumer}. \n Both the consumer {note_consumer} and the producer {note_id_prosumer} did not earn any revoltCoins."
                    else:
                        str_note = f"the consumer {note_consumer} (Blockchain ID: {note_consumer_blockchain_id}) has purchased {note_purchased_energy} kWh from the producer {note_id_prosumer} contributing to increased self-consumption within the Local Energy Community (LEC). \n As a result, consumer {note_consumer} earned {note_given_t} revoltCoins and the producer {note_id_prosumer} earned {note_prosumer_given_t} revoltCoins."
                    transaction_consumer = self.upsert_user(
                        blockchain_consumer.to_write_model(), note=str_note)
                    if transaction_consumer.is_err:
                        return transaction_consumer

                    transaction_producer = self.upsert_user(
                        blockchain_producer.to_write_model(), note=str_note)
                    if transaction_producer.is_err:
                        return transaction_producer

                    transaction_result_info_consumer: TransactionInfo = transaction_consumer.unwrap()
                    transaction_result_consumer_write_model = TransactionWriteModel(
                        prosumer_id=trade["id_prosumer"],
                        consumer_id=consumer_trading_data["id_consumer"],
                        id_transaction=transaction_result_info_consumer.tx_id,
                        purchased_energy=trade["purchased_energy"],
                        given_T=trade["given_T"],
                        received_T=trade["received_T"]
                    )
                    transactions_results.append(
                        transaction_result_consumer_write_model)
            return Ok(transactions_results)
        except Exception as e:
            return Err(e)
