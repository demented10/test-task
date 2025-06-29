import re
import sys
from collections import defaultdict

def parse_ssh_logs(log_file):
    ip_attempts = defaultdict(int)
    
    # регулярки для поиска записей
    failed_root_pattern = re.compile(
        r'Failed password for root from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    )
    repeated_pattern = re.compile(
        r'message repeated (\d+) times: \[ Failed password for root from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    )
    
    try:
        with open(log_file, 'r') as file:
            for line in file:
                # проверка на повторяющиеся сообщения
                repeated_match = repeated_pattern.search(line)
                if repeated_match:
                    attempts = int(repeated_match.group(1))
                    ip = repeated_match.group(2)
                    ip_attempts[ip] += attempts
                    continue
                
                # проверка неудачных попыток
                failed_match = failed_root_pattern.search(line)
                if failed_match:
                    ip = failed_match.group(1)
                    ip_attempts[ip] += 1
    
    except FileNotFoundError:
        print(f"error: file {log_file} not found", file=sys.stderr)
        sys.exit(1)
    
    return dict(ip_attempts)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("using: python ssh-analyser.py <log-file-name>")
        sys.exit(1)
    
    log_file = sys.argv[1]
    results = parse_ssh_logs(log_file)
    
    print(results)