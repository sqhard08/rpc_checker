4import json
import os
import subprocess
import requests
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

RPC_URLS = [
    "https://rpc.testnet-1.network/",
    "https://rpc.testnet-2.network/",
    "https://rpc.testnet-3.network/",
    "https://rpc.testnet-4.network/"
]

CONFIG_FILE_PATH = '/root/rpc/config.json'
WORKING_DIR = '/root/rpc'
CHECK_INTERVAL = 300  # 5 минут в секундах
LOG_FILE = '/root/rpc/rpc_checker.log'

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_current_rpc():
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            config = json.load(file)
        return config['wallet']['nodeRpc']
    except Exception as e:
        logging.error(f'Ошибка при чтении текущего RPC: {e}')
        return None

def update_config_json(new_node_rpc_url):
    if not os.path.exists(CONFIG_FILE_PATH):
        logging.error(f'Файл {CONFIG_FILE_PATH} не найден!')
        return False
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            config = json.load(file)
        if 'wallet' in config and 'nodeRpc' in config['wallet']:
            if config['wallet']['nodeRpc'] == new_node_rpc_url:
                logging.info(f'RPC уже установлен на {new_node_rpc_url}')
                return False
            config['wallet']['nodeRpc'] = new_node_rpc_url
            logging.info(f'Обновлено "nodeRpc" внутри "wallet" на {new_node_rpc_url}')
        with open(CONFIG_FILE_PATH, 'w') as file:
            json.dump(config, file, indent=4)
        logging.info('Изменения успешно сохранены в config.json.')
        return True
    except Exception as e:
        logging.error(f'Произошла ошибка при обновлении config.json: {e}')
        return False

def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=WORKING_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info(f'Выполнена команда: {command}')
        logging.debug(f'Вывод команды: {result.stdout}')
    except subprocess.CalledProcessError as e:
        logging.error(f'Ошибка выполнения команды {command}: {e}')
        logging.error(f'Вывод ошибки: {e.stderr}')

def check_rpc(url):
    try:
        start_time = time.time()
        response = requests.post(url, json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}, timeout=5)
        end_time = time.time()
        if response.status_code == 200:
            return url, end_time - start_time
        else:
            return url, None
    except:
        return url, None

def find_best_rpc(urls):
    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        future_to_url = {executor.submit(check_rpc, url): url for url in urls}
        results = []
        for future in as_completed(future_to_url):
            url, latency = future.result()
            if latency is not None:
                results.append((url, latency))

    if results:
        return min(results, key=lambda x: x[1])[0]
    return None

def main_loop():
    while True:
        logging.info('Начало проверки RPC')
        current_rpc = get_current_rpc()

        if current_rpc is None:
            logging.error('Не удалось получить текущий RPC')
            time.sleep(CHECK_INTERVAL)
            continue

        # Проверяем доступность текущего RPC
        _, current_latency = check_rpc(current_rpc)

        if current_latency is not None:
            logging.info(f'Текущий RPC {current_rpc} доступен. Изменения не требуются.')
        else:
            logging.warning(f'Текущий RPC {current_rpc} недоступен. Поиск альтернативы.')
            best_rpc = find_best_rpc(RPC_URLS)

            if best_rpc:
                logging.info(f'Найден лучший доступный RPC: {best_rpc}')
                if update_config_json(best_rpc):
                    run_shell_command('docker-compose down -v')
                    run_shell_command('chmod +x init.config')
                    run_shell_command('./init.config')
                    run_shell_command('docker-compose up -d')
                    logging.info(f'Переключено на новый RPC: {best_rpc}')
                else:
                    logging.info('Конфигурация не изменилась, перезапуск не требуется.')
            else:
                logging.warning('Не найдено доступных RPC.')

        logging.info(f'Ожидание {CHECK_INTERVAL} секунд до следующей проверки')
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    logging.info('Запуск скрипта проверки RPC')
    main_loop()
