import random
import string
import threading
import os
from web3 import Web3
from eth_account import Account
from colorama import Fore

# Establece las URLs de las APIs de Infura para Ethereum y Binance Smart Chain
eth_url = "https://mainnet.infura.io/v3/a054154ba62441928ead432532efe94a"
bsc_url = "https://bsc-dataseed.binance.org/"

# Crea instancias de Web3 para Ethereum y Binance Smart Chain
w3_eth = Web3(Web3.HTTPProvider(eth_url))
w3_bsc = Web3(Web3.HTTPProvider(bsc_url))

# Inicializa los contadores de claves privadas válidas e inválidas
valid_count = 0
invalid_count = 0
total_balance_eth = 0
total_balance_bnb = 0

# Crea un bloqueo para sincronizar la impresión de resultados
print_lock = threading.Lock()

# Función para consultar el saldo y validar una dirección
def check_address(private_key):
    global valid_count, invalid_count, total_balance_eth, total_balance_bnb

    account = Account.from_key(private_key)
    address = account.address
    is_valid_private_key = len(private_key) == 64

    balance_bnb_wei = w3_bsc.eth.get_balance(address)
    balance_bnb = w3_bsc.from_wei(balance_bnb_wei, 'ether')
    total_balance_bnb += balance_bnb

    balance_eth_wei = w3_eth.eth.get_balance(address)
    balance_eth = w3_eth.from_wei(balance_eth_wei, 'ether')
    total_balance_eth += balance_eth

    with print_lock:
        if is_valid_private_key:
            valid_count += 1
        else:
            invalid_count += 1

        print(Fore.RED + f"> 0x{private_key} || ETH: {balance_eth:.6f} || BNB: {balance_bnb:.6f}")

        # Verifica si el saldo de ETH y BNB es mayor o igual a 0.000000
        if balance_eth >= 0.000001 and balance_bnb >= 0.000001:
            user_input = input("¿Deseas continuar? (S/N): ").strip().lower()
            if user_input != "s":
                os._exit(0)  # Sale del programa si el usuario no desea continuar

# Solicita al usuario la cantidad de hilos a utilizar
num_threads = int(input("Ingrese la cantidad de hilos a utilizar: "))

# Crea una lista de hilos
threads = []

# Crea hilos y ejecuta la función de verificación
for _ in range(num_threads):
    private_key = ''.join(random.choices(string.hexdigits, k=64))
    thread = threading.Thread(target=check_address, args=(private_key,))
    threads.append(thread)
    thread.start()

# Espera a que todos los hilos terminen
for thread in threads:
    thread.join()

# Actualiza el título de la ventana de la consola
title = f"ETH: {total_balance_eth:.6f} - BNB: {total_balance_bnb:.6f}"
os.system(f"title {title}")
