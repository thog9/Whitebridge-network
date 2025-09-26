# Whitebridge Network Scripts 🚀

A Python script designed to automate task completion on the Whitebridge Network, such as liking, retweeting, and joining Telegram/Discord channels to earn points. Built with asyncio, aiohttp, eth_account, and colorama for efficient multi-wallet operations and a user-friendly CLI experience. Supports bilingual output (English and Vietnamese).

🔗 Register: [Whitebridge Network](https://app.whitebridge.network/referral?code=5Lhw2apM)

## ✨ Features Overview

### General Features

- **Multi-Account Support**: Reads private keys from `pvkey.txt` to perform actions across multiple accounts.
- **Colorful CLI**: Uses `colorama` for visually appealing output with colored text and borders.
- **Asynchronous Execution**: Built with `asyncio` for efficient blockchain interactions.
- **Error Handling**: Comprehensive error catching for blockchain transactions and RPC issues.
- **Bilingual Support**: Supports both English and Vietnamese output based on user selection.

### Included Scripts

1. **Auto Task**: Auto tasks on Whitebridge Network.
	-  Like campaign on X (+10 points)
	-  Retweet campaign on X (+10 points)
	-  Join Telegram (+10 points)
	-  Join Discord (+10 points)

## 🛠️ Prerequisites

Before running the scripts, ensure you have the following installed:

- Python 3.8+
- `pip` (Python package manager)
- **Dependencies**: Install via `pip install -r requirements.txt` (ensure `web3.py`, `colorama`, `asyncio`, `eth-account`, `aiohttp_socks` and `inquirer` are included).
- **pvkey.txt**: Add private keys (one per line) for wallet automation.
- **proxies.txt** (optional): Add proxy addresses for network requests, if needed.


## 📦 Installation

1. **Clone this repository:**
- Open cmd or Shell, then run the command:
```sh
git clone https://github.com/thog9/Whitebridge-network.git
```
```sh
cd Whitebridge-network
```
2. **Install Dependencies:**
- Open cmd or Shell, then run the command:
```sh
pip install -r requirements.txt
```
3. **Prepare Input Files:**
- Open the `pvkey.txt`: Add your private keys (one per line) in the root directory.
```sh
nano pvkey.txt 
```

- Create `proxies.txt` for specific operations:
```sh
nano proxies.txt
```
4. **Run:**
- Open cmd or Shell, then run command:
```sh
python main.py
```
- Choose a language (Vietnamese/English).

## 📬 Contact
Connect with us for support or updates:

- **Telegram**: [thog099](https://t.me/thog099)
- **Channel**: [CHANNEL](https://t.me/thogairdrops)
- **Group**: [GROUP CHAT](https://t.me/thogchats)
- **X**: [Thog](https://x.com/thog099) 

----

## ☕ Support Us
Love these scripts? Fuel our work with a coffee!

🔗 BUYMECAFE: [BUY ME CAFE](https://buymecafe.vercel.app/)

