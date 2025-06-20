from option import Err, Ok, Result
from pydantic import BaseModel
import numpy as np
import pandas as pd

from localres_marketplace_service.src.marketplace.data_types import (
    ConsumerData,
    ProsumerData,
    TradingData,
)


class CoreLogics(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    def apply_trading_logic(
        self, consumer_data: ConsumerData, prosumer_data: ProsumerData
    ) -> Result[TradingData, Exception]:
        try:
            # Step 1: Order in descending order ConsumerData based on thresholds and is_new
            consumer_data.consumer_data = sorted(
                consumer_data.consumer_data, key=lambda x: (-x["threshold"])
            )
            # Step 2: Calculation of Energy Offered by Each Prosumer Based on Production Percentage
            total_produced_energy = sum(
                item["produced_energy"] for item in prosumer_data.prosumer_data
            )
            total_energy_demand = sum(
                item["consumed_energy"] for item in consumer_data.consumer_data
            )
            prosumer_percentage_data = [
                {
                    "id_prosumer": item["id_prosumer"],
                    "%_produced_energy": round(
                        item["produced_energy"] / total_produced_energy, 2
                    ),
                    "energy_to_be_exchanged": np.clip(
                        round(
                            (round(item["produced_energy"] / total_produced_energy, 2))
                            * total_energy_demand,
                            1,
                        ),
                        a_min=0,
                        a_max=round(item["produced_energy"], 1),
                    ),
                }
                for item in prosumer_data.prosumer_data
            ]
            df_prosumer_percentage = pd.DataFrame(prosumer_percentage_data)
            # Step 3 Calculation of exchanged energy with each consumer
            exchanged_energy = pd.DataFrame(
                index=[item["id_consumer"] for item in consumer_data.consumer_data],
                columns=df_prosumer_percentage["id_prosumer"],
            )

            for index, row in df_prosumer_percentage.iterrows():
                remaining_energy = row["energy_to_be_exchanged"]
                for consumer in consumer_data.consumer_data:
                    ## Remove from consumer_data the consumer that is the current prosumer
                    id_consumer = consumer["id_consumer"]
                    consumed_energy = consumer["consumed_energy"]
                    produced_energy = row["%_produced_energy"]
                    prosumer_id = row["id_prosumer"]

                    if prosumer_id == id_consumer:
                        continue

                    energy = np.clip(
                        (produced_energy * consumed_energy, 1),
                        a_min=0,
                        a_max=remaining_energy,
                    )
                    remaining_energy = remaining_energy - energy[0]
                    exchanged_energy.loc[id_consumer, prosumer_id] = round(energy[0], 1)
                # Step 4 Calculation of earned tokens
                exchanged_tokens = pd.DataFrame(
                    index=[item["id_consumer"] for item in consumer_data.consumer_data],
                    columns=df_prosumer_percentage["id_prosumer"],
                )
                prosumer_tokens = pd.DataFrame(
                    index=[item["id_consumer"] for item in consumer_data.consumer_data],
                    columns=df_prosumer_percentage["id_prosumer"],
                )
                for consumer in consumer_data.consumer_data:
                    id_consumer = consumer["id_consumer"]
                    threshold = (
                        consumer["threshold"] if consumer["threshold"] != 0 else 95
                    )
                    for prosumer_id in df_prosumer_percentage["id_prosumer"]:
                        exchanged_tokens.loc[id_consumer, prosumer_id] = round(
                            exchanged_energy.loc[id_consumer, prosumer_id] * threshold,
                            1,
                        )
                        prosumer_tokens.loc[id_consumer, prosumer_id] = round(
                            exchanged_energy.loc[id_consumer, prosumer_id]
                            * (100 - threshold),
                            1,
                        )
            # RESULTS
            trading_result = [
                {
                    "id_consumer": consumer["id_consumer"],
                    "trades": [
                        {
                            "id_prosumer": prosumer_id,
                            "given_T": exchanged_tokens.loc[
                                consumer["id_consumer"], prosumer_id
                            ],
                            "purchased_energy": exchanged_energy.loc[
                                consumer["id_consumer"], prosumer_id
                            ],
                            "received_T": prosumer_tokens.loc[
                                consumer["id_consumer"], prosumer_id
                            ],
                        }
                        for prosumer_id in df_prosumer_percentage["id_prosumer"]
                        if not pd.isna(
                            exchanged_tokens.loc[consumer["id_consumer"], prosumer_id]
                        )
                        and not pd.isna(
                            prosumer_tokens.loc[consumer["id_consumer"], prosumer_id]
                        )
                    ],
                }
                for consumer in consumer_data.consumer_data
            ]
            return Ok(TradingData(trading_data=trading_result))
        except Exception as e:
            return Err(e)