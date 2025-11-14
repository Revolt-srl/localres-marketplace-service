# Localres Marketplace Service
## Overview 
This service has been deployed by [Revolt](https://revoltsrl.com) to manage the marketplace transactions between prosumers and consumers of a renewable energy community (REC) in the context of the [LocalRES Project](https://www.localres.eu/).

The service is designed to facilitate P2P energy exchange within RECs, promoting local self-consumption and user engagement within the Italian regulation framework. Energy exchanges are virtual: no physical transfer occurs. Local renewable energy is virtually assigned to members based on real-time production and consumption.

## The service
The service manages energy attribution within a REC and distributes a virtual token called RevoltCoin (RC) based on actual production and consumption data.

For each kWh of renewable energy that a consumer virtually self-consumes, 100 RCs represent the base value of that energy. Consumers participate by submitting offers indicating how many RCs they are willing to pay per kWh (denoted as N). Their net gain is calculated as the difference between the baseline (100 RC) and their offer (i.e., 100 – N RC).

Consumers who do not submit an offer are assigned a default offer of 95 RC/kWh and are matched only after active participants. All offers are ranked in descending order and available energy is assigned to the highest bidders first.

Once the matching is complete, RCs are distributed to prosumers in proportion to the renewable energy they actually produced. The RC exchange occurs after actual production and consumption, following all user-defined thresholds.

All transactions are securely recorded on a blockchain, ensuring transparency, traceability and immutability of the process.

In our architecture, what each consumer submits as an offer, i.e. the amount of RCs they are willing to leave to the prosumer for each virtually self-consumed kWh, is formally referred to as a **threshold**. This threshold defines their priority in the ranking used for energy allocation, with higher thresholds gaining precedence in the matching process.

## The architecture
<img width="801" height="615" alt="marketplace_library v3 excalidraw" src="https://github.com/user-attachments/assets/4fdecdb9-bee0-4bf0-98e0-46110f4fcb6e" />

The project is based on the framework FastAPI, on the orm SQLAlchemy and on the Algorand Blockchain.

### Data workflow
<img width="958" height="299" alt="data-workflow-localres excalidraw" src="https://github.com/user-attachments/assets/af6880d3-1749-47f8-a0d7-5c09666188f0" />


## Prerequisites
There are some prerequisites to run this project
- Docker: the service is containerized using the Docker technology, to make the project run you will need a machine with docker enabled
- An application in the Algorand Blockchain

- A PostgreSQL compatible database

- A service that will schedule the execution

### The application in the Algorand Blockchain
To register the transaction using the blockchain technology, this service need a blockchain application in the Algorand environment.

The application will need to have some subroutine like:
- update_user: to update the user data
- change_owner: to change the owner of the smart contract
- delete_user: to delete the user from the smart contract

All the information about the user must be included in a string with the following format: 

```
ps_<value_of_thresholds_encoded_as_bytes_using_utf8_padded_to_3_digits>balance_<the_balance__converted_to_an_8_byte_big_endian_format>

```

### A PostgreSQL compatbile database

We used a PostgreSQL instance of a database inside a Docker container. You can choose the database you want, just make sure that is PgSQL compatible. 
If you want to add the support to other databases feel free to open a Pull Request with the implementation!
In our case the database will need to have the following tables:
- consumption
- production
- trading_data
- users
  
#### Consumption table

```sql
CREATE TABLE consumption(
    id varchar(255) NOT NULL,
    device varchar(255),
    "value" double precision,
    timestamp timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id)
);
```
- id: the identifier of the table
- device: the code associated to the device
- value: the value of the consumption
- timestamp: the timestamp relative to the value
  


#### Production table

```sql
CREATE TABLE production(
    id varchar(255) NOT NULL,
    device varchar(255),
    "value" double precision,
    timestamp timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(id)
);
```

- id: the identifier of the table
- device: the code associated to the device
- value: the value of the production
- timestamp: the timestamp relative to the value
  
#### Trading_data table

```sql
CREATE TABLE trading_data(
    id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
    timestamp timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "value" double precision,
    consumer_id varchar(255) NOT NULL,
    prosumer_id varchar(255) NOT NULL,
    purchased_energy double precision,
    prosumer_value double precision,
    transaction_id varchar(255),
    PRIMARY KEY(id)
);
```

- id: the identifier of the record
- timestamp: the timestamp of the transaction generated
- value: the token earned by the consumer
- consumer_id: the id of the consumer
- prosumer_id: the id of the prosumer
- purchased_energy: the quantity of energy purchased
- prosumer_value: the token earned by the prosumer
- transaction_id: the id of the transaction inside the blockchain environment


#### Users table

```sql
CREATE TABLE users(
    id varchar(255) NOT NULL,
    device varchar(255),
    blockchain_id integer,
    production_device varchar(255),
    PRIMARY KEY(id)
);

```

- id: the identifier of the record
- device: the consumption device associated to the user
- blockchain_id: the id of the user inside the smart contract
- production_device: the production device associated to the user

### A service that will schedule the execution

The service DOES NOT execute every hour, you will need to use an external service to trigger the execution every hour.

In our case we use a scheduling service called [Apache Airflow](https://airflow.apache.org/) which will trigger the execution of the service every hour doing a GET REQUEST to the endpoint `marketplace/run`.

You are free to choose the solution you want, like a chron job which performs the get request mentioned before.

## Run the service
### Setup
Before running the service you will need to setup you environment variable.

Create a .env file in the root of the project based on the .env.example file and add your data
### Start
To start the service just use the command `./stack prod up -d` and you will be able to spin up a docker container with the port `18001` exposed on your network.
Visit the page `http://localhost:18001/docs` to see the endpoints

## API Documentation
The service expose the following endpoints:
### Protected on Admin Level
The following endpoints are protected using the Admin Token in the `.env` file

- DELETE `blockchain/user/{user_id}`: using the id of the user you can delete the data about if from the smart contract

- PUT `blockchain/user`: this endpoint allow you to add a user to the smart contract. For more info read the following paragraph

- GET `marketplace/run`: this endpoint trigger the execution of the marketplace algorithm. The service takes in the consideration the datetime of the execution. 

### Protected on User level
The following endpoints are protected using the Client Token in the `.env` file

- GET `blockchain/user/{user_id}`: using the id of the user you can get the data about it

- GET `blockchain/user/`: without adding the id of the user you will be able to get all the data for all the users inside the smart contract


### The INSERT/UPDATE of an User
Using the `PUT` to the endpoint `blockchain/user` it is possible to create or update an User on the Smart Contract stored in the blockchain.

The data structure to perform the action is based on the following classes:

```python
class UserViewModel(BaseModel):
    user_id: str
    balance: int
    thresholds: list[Threshold]
    is_new: bool = True


class Threshold(BaseModel):
    hour: int
    value: int # use 0 as default value

    class Config:
        arbitrary_types_allowed = True

```

## The output of the service
To see the output of the service you will need a Database Client like [DBeaver](https://dbeaver.io/) and access to the data inside the `Trading_data table`.
