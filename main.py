import paramiko
import pytest
from colorama import Fore, Style

EXPECTED_PARAMS = {
    'permitrootlogin': 'no',
    'allowtcpforwarding': 'no',
    'passwordauthentication': 'no',
    'pubkeyAuthentication': 'no'
}

SSH_HOST = ''
SSH_USER = ''
SSH_PASSWORD = ''
SSHD_CONFIG_PATH = '/etc/ssh/sshd_config'


def get_ssh_config(hostname, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)

    stdin, stdout, stderr = ssh.exec_command('sshd -T')
    runtime_config = stdout.read().decode('utf-8').splitlines()

    stdin, stdout, stderr = ssh.exec_command(f'cat {SSHD_CONFIG_PATH}')
    file_content = stdout.read().decode('utf-8').splitlines()

    ssh.close()

    return runtime_config, file_content


def parse_ssh_config(config):
    params = {}
    for line in config:
        if ' ' in line:
            key, value = line.split(' ', 1)
            params[key.lower()] = value.lower()
    return params


def parse_sshd_config_file(config_file_lines):
    params = {}
    duplicates = set()
    for line in config_file_lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if ' ' in line:
                key, value = line.split(None, 1)
                key = key.lower()
                value = value.lower()

                if key in params:
                    duplicates.add(key)
                else:
                    params[key] = value
            else:
                key = line.lower()
                if key in params:
                    duplicates.add(key)
                else:
                    params[key] = ''

    return params, duplicates


@pytest.fixture(scope="module")
def ssh_config():
    runtime_config, file_content = get_ssh_config(SSH_HOST, SSH_USER, SSH_PASSWORD)
    file_config, duplicates = parse_sshd_config_file(file_content)
    return {
        'runtime': parse_ssh_config(runtime_config),
        'file': file_config,
        'duplicates': duplicates
    }


def test_ssh_config_duplicates(ssh_config):
    duplicates = ssh_config['duplicates']
    print("")

    if duplicates:
        print(
            f"{Fore.YELLOW}WARNING: Duplicate parameters found in sshd_config: {', '.join(duplicates)}{Style.RESET_ALL}")
    else:
        assert True


def test_runtime_config(ssh_config):
    runtime_config = ssh_config['runtime']
    print("")

    for param, expected_value in EXPECTED_PARAMS.items():
        runtime_value = runtime_config.get(param.lower())
        if runtime_value is None:
            print(f"{Fore.RED}FAIL {param} is missing in runtime config{Style.RESET_ALL}")
        elif runtime_value != expected_value.lower():
            print(f"{Fore.RED}FAIL {param} is {runtime_value}, must be {expected_value}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}OK {param} is {expected_value} in runtime config{Style.RESET_ALL}")


def test_file_config(ssh_config):
    file_config = ssh_config['file']
    print("")

    for param, expected_value in EXPECTED_PARAMS.items():
        file_value = file_config.get(param.lower())
        if file_value is None:
            print(
                f"{Fore.YELLOW}WARNING {param} is not defined in file config, using default value{Style.RESET_ALL}")
        elif file_value != expected_value.lower():
            print(f"{Fore.RED}FAIL {param} is {file_value}, must be {expected_value}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}OK {param} is {expected_value} in file config{Style.RESET_ALL}")


def test_runtime_vs_file_config(ssh_config):
    file_config = ssh_config['file']
    runtime_config = ssh_config['runtime']
    differences = []
    print("")

    for param in EXPECTED_PARAMS.keys():
        runtime_value = runtime_config.get(param.lower())
        file_value = file_config.get(param.lower())

        if runtime_value != file_value and file_value is not None:
            differences.append(f"{param}: runtime={runtime_value}, file={file_value}")

    if differences:
        print(
            f"{Fore.RED}Differences were found between the current configuration and the configuration from the file. Please reload ssh.{Style.RESET_ALL}")
        for diff in differences:
            print(f"{Fore.RED}Difference: {diff}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}The configurations match.{Style.RESET_ALL}")


if __name__ == "__main__":
    pytest.main([__file__])
