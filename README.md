# 🤖 Plaza Finance Bot

A Python-based automated bot for interacting with Plaza Finance protocol on Base Sepolia testnet. The bot automates claiming from faucet and performing various token operations like creating bonds and leveraged positions.

## ✨ Features

- 🔄 Automated interaction with Plaza Finance protocol
- 🚰 Faucet claiming with verification
- 💱 Token operations (Create/Redeem for Bond and Leverage tokens)
- ⛽ Gas price monitoring and optimization
- 🔒 Proxy support
- 🔄 Automatic retries with exponential backoff
- 📝 Comprehensive logging
- 👛 Wallet rotation with configurable delays
- 🔄 Headers rotation for request anonymization

## 📋 Prerequisites

- 🐍 Python 3.8+
- 🌐 Web3.py
- 💰 Base Sepolia ETH for gas fees (minimum 0.002 ETH per wallet)
- 🔑 Plaza Finance API key

## 🚀 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd plaza-finance-bot
```

2. Install required dependencies:
```bash
pip install web3 requests asyncio colorama python-dotenv tenacity
```

3. Create and configure `.env` file:
```env
PLAZA_API_KEY=your_api_key_here
HTTP_PROXY=your_proxy_url_here  # Optional
```

4. Create `private_keys.txt` file with your wallet private keys (one per line):
```text
private_key1
private_key2
# Add more private keys as needed
```

## ⚙️ Configuration

The bot includes several configurable parameters:

- 💰 `MIN_GAS_BALANCE`: Minimum ETH balance required for gas (default: 0.002 ETH)
- ⛽ `MAX_GAS_PRICE`: Maximum acceptable gas price (default: 1 gwei)
- 🔄 Headers pool for request rotation
- 🔒 Proxy support for enhanced privacy
- ⏱️ Configurable delays between operations and wallet rotations

## 🎮 Usage

Run the bot using:
```bash
python main.py
```

The bot will:
1. 📥 Load private keys from `private_keys.txt`
2. 🔄 Process each wallet sequentially with random delays
3. For each wallet:
   - 💰 Check ETH balance for gas
   - ⛽ Monitor gas prices
   - 🚰 Claim from faucet if needed
   - ✅ Set token approvals
   - 💱 Perform create/redeem operations for both bond and leverage tokens
4. ⏰ Wait 6 hours before starting the next cycle

## 📜 Contract Addresses

- 🪙 WSTETH Token: `0x13e5fb0b6534bb22cbc59fae339dbbe0dc906871`
- 📊 Plaza Finance Contract: `0x47129e886b44B5b8815e6471FCD7b31515d83242`

## ⚠️ Error Handling

The bot includes comprehensive error handling:
- 🔄 Automatic retries for failed operations
- ⏳ Exponential backoff for rate limiting
- 📝 Detailed logging to `plaza_bot.log`
- 🛡️ Cloudflare detection and handling
- ⌛ Transaction timeout handling

## 📝 Logging

Logs are written to both console and `plaza_bot.log` file, including:
- ✅ Operation status and transaction hashes
- ❌ Error messages and stack traces
- ⛽ Gas prices and balance information
- ⏱️ Timing information for operations

## 🔒 Safety Features

- ⛽ Gas price monitoring to prevent overspending
- 💰 Balance checks before operations
- ✅ Transaction confirmation monitoring
- ⏱️ Configurable delays to prevent rate limiting
- 🔒 Proxy support for enhanced privacy

## 📊 Monitoring

The bot provides real-time console output with color-coded status messages:
- 🟢 Green: Success messages
- 🟡 Yellow: Warning and info messages
- 🔴 Red: Error messages

## 🛑 Stopping the Bot

The bot can be stopped safely by pressing `Ctrl+C`. It will complete the current operation before shutting down.

## ⚠️ Disclaimer

This bot is for educational purposes only. Make sure to:
- 🧪 Test thoroughly on testnet before using
- 📖 Review and understand the code before running
- 🔒 Never share your private keys
- ⚠️ Use at your own risk

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🔧 Support

If you encounter any issues or have questions, please:
- 📝 Open an issue in the repository
- 📧 Contact the development team
- 📚 Check the documentation

## 🙏 Acknowledgements

- 🌐 Plaza Finance team for the protocol
- 🛠️ Web3.py developers
- 👥 All contributors to this project