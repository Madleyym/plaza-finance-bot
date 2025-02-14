import web3
import requests
import asyncio
import random
import json
import os
from datetime import datetime
from colorama import Fore, Style, init
from decimal import Decimal
from eth_account import Account
from web3.exceptions import ContractLogicError
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Initialize colorama for colored logging
init(autoreset=True)

# Current information
CURRENT_TIME = "2025-02-14 03:44:55"
CURRENT_USER = "Madleyym"


class PlazaFinanceBot:
    def __init__(self):
        # Headers pool for rotation
        self.headers_pool = [
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/json",
                "Origin": "https://plaza.finance",
                "Referer": "https://plaza.finance/",
                "Connection": "keep-alive",
                "SEC-CH-UA": '"Not A(Brand";v="99", "Google Chrome";v="121"',
            },
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/json",
                "Origin": "https://plaza.finance",
                "Referer": "https://plaza.finance/",
                "Connection": "keep-alive",
                "SEC-CH-UA": '"Safari";v="605.1.15"',
            }
        ]

        # Add proxy support
        self.proxy = os.getenv("HTTP_PROXY")  # Set your proxy in .env file
        self.proxies = {
            "http": self.proxy,
            "https": self.proxy
        } if self.proxy else None

        # Initialize Web3 and contracts
        self.w3 = web3.Web3(web3.HTTPProvider("https://sepolia.base.org"))
        self.WSTETH_ADDRESS = self.w3.to_checksum_address(
            "0x13e5fb0b6534bb22cbc59fae339dbbe0dc906871"
        )
        self.CONTRACT_ADDRESS = self.w3.to_checksum_address(
            "0x47129e886b44B5b8815e6471FCD7b31515d83242"
        )
        self.MIN_GAS_BALANCE = self.w3.to_wei(
            0.002, "ether"
        )  # Minimum 0.002 ETH for gas
        self.PLAZA_API_KEY = os.getenv(
            "PLAZA_API_KEY", "bfc7b70e-66ad-4524-9bb6-733716c4da94"
        )

        # Load ABIs
        self.CONTRACT_ABI = self.load_contract_abi()
        self.ERC20_ABI = self.load_erc20_abi()

        # Initialize contracts
        self.pool_contract = self.w3.eth.contract(
            address=self.CONTRACT_ADDRESS, abi=self.CONTRACT_ABI
        )
        self.wsteth_contract = self.w3.eth.contract(
            address=self.WSTETH_ADDRESS, abi=self.ERC20_ABI
        )

        print(f"{Fore.GREEN}Bot initialized successfully")
        print(f"{Fore.YELLOW}Current time: {CURRENT_TIME}")
        print(f"{Fore.YELLOW}User: {CURRENT_USER}")
        if self.proxy:
            print(f"{Fore.YELLOW}Using proxy: {self.proxy}")

    @staticmethod
    def load_contract_abi():
        return [
            {
                "inputs": [],
                "name": "bondToken",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [],
                "name": "lToken",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [
                    {
                        "internalType": "enum Pool.TokenType",
                        "name": "tokenType",
                        "type": "uint8",
                    },
                    {
                        "internalType": "uint256",
                        "name": "depositAmount",
                        "type": "uint256",
                    },
                    {"internalType": "uint256", "name": "minAmount", "type": "uint256"},
                ],
                "name": "create",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [
                    {
                        "internalType": "enum Pool.TokenType",
                        "name": "tokenType",
                        "type": "uint8",
                    },
                    {
                        "internalType": "uint256",
                        "name": "depositAmount",
                        "type": "uint256",
                    },
                    {"internalType": "uint256", "name": "minAmount", "type": "uint256"},
                ],
                "name": "redeem",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function",
            },
        ]

    @staticmethod
    def load_erc20_abi():
        return [
            {
                "constant": True,
                "inputs": [
                    {"name": "_owner", "type": "address"},
                    {"name": "_spender", "type": "address"},
                ],
                "name": "allowance",
                "outputs": [{"name": "remaining", "type": "uint256"}],
                "type": "function",
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_spender", "type": "address"},
                    {"name": "_value", "type": "uint256"},
                ],
                "name": "approve",
                "outputs": [{"name": "success", "type": "bool"}],
                "type": "function",
            },
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function",
            },
        ]

    async def check_gas_price(self):
        """Check if gas price is reasonable"""
        try:
            current_gas_price = self.w3.eth.gas_price
            max_acceptable_gas = self.w3.to_wei(1, "gwei")  # 1 gwei max
            is_acceptable = current_gas_price <= max_acceptable_gas

            print(f"{Fore.YELLOW}Current gas price: {self.w3.from_wei(current_gas_price, 'gwei')} gwei")
            print(f"{Fore.YELLOW}Max acceptable: {self.w3.from_wei(max_acceptable_gas, 'gwei')} gwei")

            return is_acceptable
        except Exception as e:
            print(f"{Fore.RED}Error checking gas price: {str(e)}")
            return False

    async def wait_for_transaction(self, tx_hash, description):
        """Wait for transaction confirmation with timeout"""
        timeout = 300  # 5 minutes timeout
        start_time = datetime.now()

        while (datetime.now() - start_time).seconds < timeout:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt is not None:
                    if receipt["status"] == 1:
                        print(
                            f"{Fore.GREEN}✓ {description} successful: {tx_hash.hex()}"
                        )
                        return True
                    else:
                        print(f"{Fore.RED}✗ {description} failed: {tx_hash.hex()}")
                        return False
            except Exception as e:
                print(f"{Fore.YELLOW}Waiting for {description} confirmation...")
            await asyncio.sleep(5)

        print(f"{Fore.RED}Transaction timeout: {description}")
        return False

    async def check_token_balance(self, token_address, wallet_address, min_balance):
        """Check if wallet has sufficient token balance"""
        try:
            token_contract = self.w3.eth.contract(address=token_address, abi=self.ERC20_ABI)
            balance = token_contract.functions.balanceOf(wallet_address).call()
            return balance >= min_balance
        except Exception as e:
            print(f"{Fore.RED}Error checking token balance: {str(e)}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def claim_faucet(self, address):
        """Claim faucet with verification and improved headers"""
        try:
            if self.proxy:
                print(f"{Fore.YELLOW}Using proxy: {self.proxy}")

            session = requests.Session()
            headers = random.choice(self.headers_pool)
            headers["x-plaza-api-key"] = self.PLAZA_API_KEY
            session.headers.update(headers)

            # Simulate real browser behavior
            try:
                await asyncio.sleep(random.uniform(3, 7))
                session.get(
                    "https://plaza.finance",
                    proxies=self.proxies,
                    timeout=30
                )
            except:
                pass

            # Add delay before request
            await asyncio.sleep(random.uniform(5, 10))

            response = session.post(
                "https://api.plaza.finance/faucet/queue",
                json={"address": address},
                timeout=30,
                proxies=self.proxies
            )

            if response.status_code == 403:
                print(f"{Fore.YELLOW}Cloudflare detected, waiting 60s...")
                await asyncio.sleep(60)
                return False

            if response.status_code == 200:
                print(f"{Fore.GREEN}Faucet claim initiated for {address}")
                return await self.verify_faucet_claim(address)

            print(f"{Fore.RED}Unexpected status: {response.status_code}")
            return False

        except Exception as error:
            print(f"{Fore.RED}Error claiming faucet: {str(error)}")
            await asyncio.sleep(30)
            return False

    async def verify_faucet_claim(self, address):
        """Verify if faucet tokens were received"""
        max_attempts = 40
        check_interval = 10

        for i in range(max_attempts):
            try:
                if await self.check_token_balance(
                    self.WSTETH_ADDRESS,
                    address,
                    self.w3.to_wei(0.008, "ether")
                ):
                    print(f"{Fore.GREEN}Faucet tokens received!")
                    return True

                print(f"{Fore.YELLOW}Waiting for tokens... ({i+1}/{max_attempts})")
                await asyncio.sleep(check_interval)

            except Exception as e:
                print(f"{Fore.YELLOW}Error checking balance: {str(e)}")
                await asyncio.sleep(5)

        return False

    async def process_wallet(self, private_key, wallet_index, total_wallets):
        """Process a single wallet with comprehensive error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                account = self.w3.eth.account.from_key(private_key)
                wallet_address = account.address

                print(
                    f"\n{Fore.YELLOW}=== Processing Wallet {wallet_index}/{total_wallets}: {wallet_address} ==="
                )

                # Check ETH balance
                eth_balance = self.w3.eth.get_balance(wallet_address)
                if eth_balance < self.MIN_GAS_BALANCE:
                    print(
                        f"{Fore.RED}Insufficient ETH for gas. Need {self.w3.from_wei(self.MIN_GAS_BALANCE, 'ether')} ETH"
                    )
                    return False

                # Check gas price
                if not await self.check_gas_price():
                    print(f"{Fore.RED}Gas price too high, skipping wallet")
                    return False

                # Claim faucet and verify
                if not await self.claim_faucet(wallet_address):
                    if attempt < max_retries - 1:
                        wait_time = random.uniform(60, 180)
                        print(f"{Fore.YELLOW}Retrying in {int(wait_time)}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    return False

                # Set unlimited approval
                try:
                    allowance = self.wsteth_contract.functions.allowance(
                        wallet_address, self.CONTRACT_ADDRESS
                    ).call()
                    if allowance < self.w3.to_wei(1, "ether"):
                        approve_tx = await self.approve_token(private_key)
                        if not approve_tx:
                            print(f"{Fore.RED}Approval failed, skipping wallet")
                            return False
                except Exception as e:
                    print(f"{Fore.RED}Error checking/setting approval: {str(e)}")
                    return False

                # Perform operations
                operations = [
                    ("create", 0),  # Create Bond
                    ("create", 1),  # Create Leverage
                    ("redeem", 0),  # Redeem Bond
                    ("redeem", 1),  # Redeem Leverage
                ]

                for operation, token_type in operations:
                    success = await self.perform_operation(
                        operation, token_type, private_key
                    )
                    if not success:
                        print(
                            f"{Fore.RED}{operation.capitalize()} operation failed for token type {token_type}"
                        )
                        continue
                    await asyncio.sleep(random.uniform(10, 20))

                return True

            except Exception as e:
                print(f"{Fore.RED}Error on attempt {attempt + 1}/3: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(random.uniform(30, 60))

        return False

    async def approve_token(self, private_key):
        """Approve token spending"""
        account = self.w3.eth.account.from_key(private_key)
        max_uint = 2**256 - 1

        try:
            approve_txn = self.wsteth_contract.functions.approve(
                self.CONTRACT_ADDRESS, max_uint
            )
            signed_txn = await self.build_and_sign_tx(
                approve_txn, account.address, private_key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            return await self.wait_for_transaction(tx_hash, "Token approval")
        except Exception as e:
            print(f"{Fore.RED}Approval error: {str(e)}")
            return False

    async def build_and_sign_tx(self, transaction, from_address, private_key):
        """Build and sign transaction with current gas price"""
        try:
            gas_estimate = await transaction.estimate_gas({"from": from_address})
            gas_price = self.w3.eth.gas_price
            chain_id = self.w3.eth.chain_id

            transaction_data = transaction.build_transaction(
                {
                    "from": from_address,
                    "gas": int(gas_estimate * 1.2),  # Add 20% buffer
                    "gasPrice": gas_price,
                    "nonce": self.w3.eth.get_transaction_count(from_address),
                    "chainId": chain_id,
                }
            )

            return self.w3.eth.account.sign_transaction(transaction_data, private_key)
        except Exception as e:
            print(f"{Fore.RED}Error building transaction: {str(e)}")
            raise

    async def perform_operation(self, operation, token_type, private_key):
        """Perform create or redeem operation with retries"""
        account = self.w3.eth.account.from_key(private_key)
        max_retries = 3

        for attempt in range(max_retries):
            try:
                print(
                    f"{Fore.YELLOW}Attempting {operation} for token type {token_type} (attempt {attempt + 1}/{max_retries})"
                )

                if operation == "create":
                    amount = self.w3.to_wei(random.uniform(0.009, 0.01), "ether")
                    transaction = self.pool_contract.functions.create(
                        token_type, amount, 0
                    )
                    print(
                        f"{Fore.YELLOW}Creating with amount: {self.w3.from_wei(amount, 'ether')} ETH"
                    )
                else:  # redeem
                    token_address = await self.get_token_address(token_type)
                    balance = await self.get_token_balance(
                        token_address, account.address
                    )
                    if balance == 0:
                        print(
                            f"{Fore.YELLOW}No balance to redeem for token type {token_type}"
                        )
                        return True
                    amount = balance // 2
                    transaction = self.pool_contract.functions.redeem(
                        token_type, amount, 0
                    )
                    print(
                        f"{Fore.YELLOW}Redeeming amount: {self.w3.from_wei(amount, 'ether')} tokens"
                    )

                signed_tx = await self.build_and_sign_tx(
                    transaction, account.address, private_key
                )
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                success = await self.wait_for_transaction(
                    tx_hash, f"{operation} {token_type}"
                )

                if success:
                    return True

            except Exception as e:
                print(
                    f"{Fore.RED}{operation.capitalize()} attempt {attempt + 1} failed: {str(e)}"
                )
                if attempt < max_retries - 1:
                    wait_time = random.uniform(10, 20)
                    print(
                        f"{Fore.YELLOW}Waiting {int(wait_time)}s before next attempt..."
                    )
                    await asyncio.sleep(wait_time)

        return False

    async def get_token_address(self, token_type):
        """Get token contract address based on type"""
        try:
            if token_type == 0:
                return self.pool_contract.functions.bondToken().call()
            return self.pool_contract.functions.lToken().call()
        except Exception as e:
            print(f"{Fore.RED}Error getting token address: {str(e)}")
            raise

    async def get_token_balance(self, token_address, wallet_address):
        """Get token balance"""
        try:
            token_contract = self.w3.eth.contract(
                address=token_address, abi=self.ERC20_ABI
            )
            return token_contract.functions.balanceOf(wallet_address).call()
        except Exception as e:
            print(f"{Fore.RED}Error getting token balance: {str(e)}")
            raise
