import platform
import subprocess
from venv import logger

from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import base64
import os

class LicenseControl:
    def __init__(self, key=None):
        if key is None:
            key = Fernet.generate_key()
        self.key = key
        self.cipher_suite = Fernet(self.key)

    # 获取主板时间
    @staticmethod
    def get_system_bios_time():
        system = platform.system().lower()  # 获取操作系统类型

        if system == "windows":
            # Windows 系统：使用 wmic 获取 BIOS 时间
            try:
                result = subprocess.check_output(
                    "wmic path Win32_OperatingSystem get LastBootUpTime",
                    shell=True,
                    text=True
                )
                bios_time = result.splitlines()[1].strip().split(".")[0]
                return bios_time
            except Exception as e:
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        elif system == "linux":
            # Linux 系统：使用 dmidecode 获取 BIOS 时间
            try:
                result = subprocess.check_output(
                    "sudo dmidecode -t bios | grep 'Release Date'",
                    shell=True,
                    text=True
                )
                bios_time = result.split(":")[1].strip()
                return bios_time
            except Exception as e:
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        elif system == "darwin":  # macOS
            # macOS 系统：使用 system_profiler 获取 BIOS 时间
            try:
                result = subprocess.check_output(
                    "sudo system_profiler SPHardwareDataType | grep 'Boot ROM Version'",
                    shell=True,
                    text=True
                )
                bios_time = result.split(":")[1].strip()
                return bios_time
            except Exception as e:
                return datetime.now().strftime("%Y-%m-%d")
        else:
            return "Unsupported operating system."

    def calculate_future_date(self, base_time, days):
        """
        基于指定时间计算往后推迟指定天数的日期
        :param base_time: 基础时间（datetime 对象）
        :param days: 推迟的天数
        :return: 推迟后的日期（格式：YYYY-MM-DD）
        """
        try:
            future_date = datetime.strptime(base_time, "%Y-%m-%d") + timedelta(days=days)
            return future_date
        except Exception as e:
            return f"Error calculating future date: {e}"

    def generate_license(self, expiration_days, output_file='LICENSE'):
        expiration_date = self.calculate_future_date(self.get_system_bios_time(), expiration_days)
        expiration_date_str = expiration_date.isoformat()
        encrypted_data = self.cipher_suite.encrypt(expiration_date_str.encode())
        with open(output_file, 'wb') as license_file:
            license_file.write(encrypted_data)
        logger.info(f"License file '{output_file}' generated successfully.")
        return self.key

    def decrypt_license(self, license_file='LICENSE'):
        with open(license_file, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        expiration_date_str = decrypted_data.decode()
        expiration_date = datetime.fromisoformat(expiration_date_str)
        return datetime.strftime(expiration_date, "%Y-%m-%d")

    @staticmethod
    def validate_license(key, license_file='LICENSE'):
        def decorator(func):
            def wrapper(*args, **kwargs):
                manager = LicenseControl(key)
                expiration_date = manager.decrypt_license(license_file)
                if manager.get_system_bios_time() < expiration_date:
                    return func(*args, **kwargs)
                else:
                    raise Exception("License has expired.")
            return wrapper
        return decorator

# Example usage:
if __name__ == "__main__":
    # 生成合法的 Fernet 密钥
    key = "mxey3_GNnYDQXsIxK4NABQ0eqmr47coXJLKLkqcdpjU="
    # manager = LicenseControl(key=key)
    # manager.generate_license(expiration_days=30, output_file='LICENSE')

    LM = LicenseControl(key)
    print(LM.decrypt_license('/Users/chenshuhang/PycharmProjects/license_manager/LICENSE'))
    # @LM.validate_license(key, '/Users/chenshuhang/PycharmProjects/license_manager/LICENSE')
    # def some_function():
    #     print("License is valid. Function executed.")

    # some_function()