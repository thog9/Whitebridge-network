import os
import sys
import asyncio
import json
import random
import string
from typing import List, Tuple
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_account.messages import encode_defunct
from colorama import init, Fore, Style
import aiohttp
from aiohttp_socks import ProxyConnector
import datetime
from datetime import UTC

# Initialize colorama
init(autoreset=True)

# Border width
BORDER_WIDTH = 80

API_BASE_URL = "https://networkapi-2snbrq2o3a-ue.a.run.app"
WALLET_NONCE_URL = f"{API_BASE_URL}/wallet/nonce"
WALLET_SIGNIN_URL = f"{API_BASE_URL}/wallet/signin"
TASKS_URL = f"{API_BASE_URL}/points/tasks"
IP_CHECK_URL = "https://api.ipify.org?format=json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "Content-Type": "application/json",
    "Origin": "https://app.whitebridge.network",
    "Referer": "https://app.whitebridge.network/",
    "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site"
}

# Configuration
CONFIG = {
    "DELAY_BETWEEN_ACCOUNTS": 5,  # Seconds
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 3,  # Seconds
    "THREADS": 2,
    "TIMEOUT": 30  # Seconds
}

# List of tasks to complete
TASKS = [
    {"taskId": "like-campaign-on-x", "points": 10},
    {"taskId": "join-telegram", "points": 10},
    {"taskId": "retweet-campaign-on-x", "points": 10},
    {"taskId": "join-discord", "points": 10}
]

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'TỰ ĐỘNG HOÀN THÀNH NHIỆM VỤ - WHITEBRIDGE NETWORK',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'proxies': 'proxy trong proxies.txt',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'loading_private_key': 'Đang tải private key: {private_key}',
        'wallet_address': 'Địa chỉ ví: {address}',
        'signing_message': 'Đang ký thông điệp...',
        'sign_in_success': '✅ Đăng nhập thành công!',
        'sign_in_failure': '❌ Đăng nhập thất bại: {error}',
        'completing_task': 'Đang hoàn thành nhiệm vụ: {task}',
        'task_success': '✅ Hoàn thành nhiệm vụ {task} (+{points} điểm)',
        'task_failure': '❌ Thất bại khi hoàn thành nhiệm vụ {task}: {error}',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '✔ HOÀN THÀNH: {successful}/{total} ĐĂNG NHẬP VÀ HOÀN THÀNH NHIỆM VỤ',
        'error': 'Lỗi',
        'wallets_to_process': 'Số ví sẽ xử lý từ pvkey.txt: {count}',
        'no_private_keys': 'Không tìm thấy private key trong pvkey.txt'
    },
    'en': {
        'title': 'AUTOMATIC TASK COMPLETION - WHITEBRIDGE NETWORK',
        'info': 'Information',
        'found': 'Found',
        'proxies': 'proxies in proxies.txt',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with public IP - [{public_ip}]',
        'no_proxy': 'No proxy',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or non-working proxy: {proxy}',
        'ip_check_failed': '⚠ Unable to check public IP: {error}',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'loading_private_key': 'Loading private key: {private_key}',
        'wallet_address': 'Wallet address: {address}',
        'signing_message': 'Signing message...',
        'sign_in_success': '✅ Login successful!',
        'sign_in_failure': '❌ Login failed: {error}',
        'completing_task': 'Completing task: {task}',
        'task_success': '✅ Completed task {task} (+{points} points)',
        'task_failure': '❌ Failed to complete task {task}: {error}',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '✔ COMPLETED: {successful}/{total} LOGIN AND TASK COMPLETION',
        'error': 'Error',
        'wallets_to_process': 'Number of wallets to process from pvkey.txt: {count}',
        'no_private_keys': 'No private keys found in pvkey.txt'
    }
}

# Display functions
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

def print_message(message: str, color=Fore.YELLOW):
    print(f"{color}{message}{Style.RESET_ALL}")

def print_wallets_summary(count: int, language: str = 'vi'):
    print_border(
        LANG[language]['processing_wallets'].format(count=count),
        Fore.MAGENTA
    )
    print()

# Utility functions
def load_proxies(file_path: str = "proxies.txt", language: str = 'vi'):
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW} ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add proxies here, one per line\n# Example: socks5://user:pass@host:port or http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not proxy.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print(f"{Fore.YELLOW} ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.YELLOW} ℹ {LANG[language]['found']} {len(proxies)} {LANG[language]['proxies']}{Style.RESET_ALL}")
        return proxies
    except Exception as e:
        print(f"{Fore.RED} ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'vi') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW} ⚠ {LANG[language]['no_private_keys']}. Creating new file.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add private keys here, one per line\n# Example: 0xabcdef...\n")
            return []
        
        private_keys = []
        with open(file_path, 'r') as f:
            for line in f:
                pk = line.strip()
                if pk and not pk.startswith('#'):
                    private_keys.append(pk)
        
        if not private_keys:
            print(f"{Fore.RED} ✖ {LANG[language]['no_private_keys']}{Style.RESET_ALL}")
            sys.exit(1)
        
        print(f"{Fore.YELLOW} ℹ {LANG[language]['found']} {len(private_keys)} private keys in pvkey.txt{Style.RESET_ALL}")
        return private_keys
    except Exception as e:
        print(f"{Fore.RED} ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

async def get_proxy_ip(proxy: str = None, language: str = 'vi') -> str:
    try:
        connector = ProxyConnector.from_url(proxy) if proxy else None
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
            async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('ip', LANG[language]['unknown'])
                print(f"{Fore.YELLOW} ⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                return LANG[language]['unknown']
    except Exception as e:
        print(f"{Fore.YELLOW} ⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}{Style.RESET_ALL}")
        return LANG[language]['unknown']

async def get_nonce(address: str, language: str = 'vi', proxy: str = None) -> str:
    headers = HEADERS.copy()
    payload = {"address": address}
    for attempt in range(CONFIG['RETRY_ATTEMPTS']):
        try:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                async with session.post(WALLET_NONCE_URL, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("nonce", "")
                    print(f"{Fore.RED} ✖ {LANG[language]['sign_in_failure'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return ""
        except Exception as e:
            if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                await asyncio.sleep(CONFIG['RETRY_DELAY'])
                continue
            print(f"{Fore.RED} ✖ {LANG[language]['sign_in_failure'].format(error=str(e))}{Style.RESET_ALL}")
            return ""
    return ""

async def sign_in(address: str, account: LocalAccount, wallet_index: int, language: str = 'vi', proxy: str = None) -> str:
    print(f"{Fore.CYAN} > {LANG[language]['signing_message']}{Style.RESET_ALL}")
    
    nonce = await get_nonce(address, language, proxy)
    if not nonce:
        print(f"{Fore.RED} ✖ {LANG[language]['sign_in_failure'].format(error='Unable to fetch nonce')}{Style.RESET_ALL}")
        return ""
    
    message = f"app.whitebridge.network wants you to sign in with your Ethereum account:\n{address}\n\nSign this message to connect with app.whitebridge.network.\n\nURI: https://app.whitebridge.network\nVersion: 1\nChain ID: 56\nNonce: {nonce}\nIssued At: {datetime.datetime.now(UTC).isoformat()}Z"
    encoded_message = encode_defunct(text=message)
    signature = account.sign_message(encoded_message).signature.hex()
    if not signature.startswith('0x'):
        signature = '0x' + signature
    
    payload = {"message": message, "signature": signature}
    headers = HEADERS.copy()
    
    for attempt in range(CONFIG['RETRY_ATTEMPTS']):
        try:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                async with session.post(WALLET_SIGNIN_URL, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        token = data.get("token", "")
                        print(f"{Fore.GREEN} ✔ {LANG[language]['sign_in_success']}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}    - {LANG[language]['wallet_address'].format(address=address)}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}    - Token: {token[:20]}...{Style.RESET_ALL}")
                        return token
                    else:
                        error_text = await response.text()
                        print(f"{Fore.RED} ✖ {LANG[language]['sign_in_failure'].format(error=f'HTTP {response.status}: {error_text}')}{Style.RESET_ALL}")
                        return ""
        except Exception as e:
            if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                delay = CONFIG['RETRY_DELAY']
                print(f"{Fore.RED} ✖ {LANG[language]['sign_in_failure'].format(error=str(e))}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED} ✖ {LANG[language]['sign_in_failure'].format(error=str(e))}{Style.RESET_ALL}")
            return ""
    return ""

async def complete_task(token: str, task: dict, language: str = 'vi', proxy: str = None) -> bool:
    print(f"{Fore.CYAN} > {LANG[language]['completing_task'].format(task=task['taskId'])}{Style.RESET_ALL}")
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    payload = {"taskId": task['taskId'], "points": task['points']}
    
    for attempt in range(CONFIG['RETRY_ATTEMPTS']):
        try:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                async with session.post(TASKS_URL, headers=headers, json=payload) as response:
                    if response.status == 200:
                        print(f"{Fore.GREEN} ✔ {LANG[language]['task_success'].format(task=task['taskId'], points=task['points'])}{Style.RESET_ALL}")
                        return True
                    print(f"{Fore.RED} ✖ {LANG[language]['task_failure'].format(task=task['taskId'], error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return False
        except Exception as e:
            if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                await asyncio.sleep(CONFIG['RETRY_DELAY'])
                continue
            print(f"{Fore.RED} ✖ {LANG[language]['task_failure'].format(task=task['taskId'], error=str(e))}{Style.RESET_ALL}")
            return False
    return False

async def process_wallet(index: int, private_key: str, language: str = 'vi', proxies: List[str] = None) -> bool:
    proxy = proxies[index % len(proxies)] if proxies else None
    print_border(f"{LANG[language]['processing_wallets'].format(count=index + 1)}", Fore.YELLOW)
    
    # Load wallet from private key
    print(f"{Fore.CYAN} > {LANG[language]['loading_private_key'].format(private_key=private_key[:10] + '...' + private_key[-10:])}{Style.RESET_ALL}")
    try:
        account = Account.from_key(private_key)
        address = account.address
        print(f"{Fore.GREEN} ✔ {LANG[language]['wallet_address'].format(address=address)}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED} ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return False
    
    # Display proxy info
    public_ip = await get_proxy_ip(proxy, language)
    proxy_display = proxy if proxy else LANG[language]['no_proxy']
    print(f"{Fore.CYAN} 🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

    # Sign in
    token = await sign_in(address, account, index + 1, language, proxy)
    if not token:
        print(f"{Fore.RED} ✖ {LANG[language]['sign_in_failure'].format(error='Login failed for wallet ' + str(index + 1))}{Style.RESET_ALL}")
        return False

    # Complete tasks
    for task in TASKS:
        if not await complete_task(token, task, language, proxy):
            print(f"{Fore.RED} ✖ {LANG[language]['task_failure'].format(task=task['taskId'], error='Failed for wallet ' + str(index + 1))}{Style.RESET_ALL}")
            return False
        await asyncio.sleep(1)  # Small delay between tasks

    return True

async def run_autotask(language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    # Load proxies
    proxies = load_proxies('proxies.txt', language)
    print()

    # Load private keys
    private_keys = load_private_keys('pvkey.txt', language)
    wallet_count = len(private_keys)

    print(f"{Fore.YELLOW} ℹ {LANG[language]['wallets_to_process'].format(count=wallet_count)}{Style.RESET_ALL}")
    print()

    print_separator()
    print_wallets_summary(wallet_count, language)

    total_processed = 0
    successful_processed = 0
    semaphore = asyncio.Semaphore(CONFIG['THREADS'])

    async def sem_process_wallet(index: int):
        nonlocal successful_processed, total_processed
        async with semaphore:
            try:
                success = await process_wallet(index, private_keys[index], language, proxies)
                total_processed += 1
                if success:
                    successful_processed += 1
                if index < wallet_count - 1:
                    delay = CONFIG['DELAY_BETWEEN_ACCOUNTS']
                    print_message(f" ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                    await asyncio.sleep(delay)
            except Exception as e:
                print(f"{Fore.RED} ✖ {LANG[language]['error']}: Processing wallet {index + 1}: {str(e)}{Style.RESET_ALL}")
                total_processed += 1

    tasks = [sem_process_wallet(i) for i in range(wallet_count)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_processed, total=total_processed)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_autotask('vi'))
