
---

# Проверка конфигурации SSH сервера

Этот скрипт с использованием `paramiko` и `pytest` проверяет настройки конфигурации SSH сервера. Скрипт выполняет подключение к удаленному серверу, получает активные параметры `sshd` и сравнивает их с конфигурацией файла `/etc/ssh/sshd_config`, выявляя расхождения и дублирующиеся параметры.

## Установка

1. Установите зависимости:
    ```bash
    pip install paramiko pytest colorama
    ```

2. Убедитесь, что у вас есть доступ к целевому серверу SSH и права на чтение файла `sshd_config`.

## Настройка

Внесите данные подключения к серверу в переменные:
```python
SSH_HOST = 'your_server_ip'
SSH_USER = 'your_ssh_user'
SSH_PASSWORD = 'your_ssh_password'
```

Также при необходимости можно изменить путь к файлу `sshd_config`:
```python
SSHD_CONFIG_PATH = '/etc/ssh/sshd_config'
```

## Описание скрипта

### Основные функции

- `get_ssh_config`: Выполняет подключение к серверу и получает активные параметры `sshd` и содержимое файла `sshd_config`.
- `parse_ssh_config`: Преобразует строковый вывод параметров в словарь.
- `parse_sshd_config_file`: Читает файл конфигурации `sshd_config`, создавая словарь параметров и фиксируя дублирующиеся записи.

### Ожидаемые параметры

Конфигурация проверяется на следующие значения (их можно изменить в коде):
```python
EXPECTED_PARAMS = {
    'permitrootlogin': 'no',
    'allowtcpforwarding': 'no',
    'passwordauthentication': 'no',
    'pubkeyAuthentication': 'no'
}
```

### Тесты

1. **`test_ssh_config_duplicates`** — проверяет наличие дублирующихся параметров в файле конфигурации.
2. **`test_runtime_config`** — проверяет, что активные параметры соответствуют ожидаемым.
3. **`test_file_config`** — проверяет, что значения параметров в `sshd_config` соответствуют ожидаемым.
4. **`test_runtime_vs_file_config`** — сравнивает активные параметры и параметры в файле конфигурации.

### Запуск

Для запуска тестов используйте команду:
```bash
python <название_скрипта>.py
```

## Примечания

- Скрипт использует `colorama` для цветного отображения результатов, что облегчает восприятие вывода.
- Если обнаружены несоответствия или дублирующиеся параметры, об этом будет выведено предупреждение.

--- 
