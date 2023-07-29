import getpass
from eth_account import Account
from web3 import Web3

def check_password():
    # Pide al usuario que ingrese la contraseña
    password = getpass.getpass("Ingrese la contraseña: ")

    # Define la contraseña que permitirá ejecutar el código
    correct_password = "Rojas17"

    # Verifica si la contraseña ingresada es correcta
    if password == correct_password:
        return True
    else:
        return False

def generate_ethereum_address():
    # Genera una clave privada aleatoria
    private_key = Account.create().key.hex()

    # Crea una instancia de cuenta a partir de la clave privada
    account = Account.from_key(private_key)

    # Obtiene la dirección Ethereum
    address = account.address

    return address, private_key

def get_eth_balance(address):
    # Conectarse a la red Ethereum a través de un proveedor de nodo o Infura
    w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/a054154ba62441928ead432532efe94a'))

    # Obtener el saldo de ETH de la dirección
    balance = w3.eth.get_balance(address)
    return w3.from_wei(balance, 'ether')

if __name__ == "__main__":
    if check_password():
        num_addresses = 1000000

        print(f"Generando {num_addresses} direcciones con sus claves privadas y saldos de Ethereum...\n")

        for i in range(num_addresses):
            address, private_key = generate_ethereum_address()
            eth_balance = get_eth_balance(address)
            print(f"Address: {address} | Private key: {private_key} | Saldo ETH: {eth_balance:.6f} ETH")

    else:
        print("Contraseña incorrecta. El programa se cerrará.")


