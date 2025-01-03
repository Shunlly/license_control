import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
import base64
import hashlib
from cryptography.fernet import Fernet


@dataclass
class License:
    """
    许可证类，表示一个完整的软件许可证
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_name: str = ''
    product_name: str = ''
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    max_devices: int = 1
    current_devices: int = 0
    features: List[str] = field(default_factory=list)
    status: str = 'active'
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        初始化后的处理，如设置过期时间
        """
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(days=365)

    def is_valid(self) -> bool:
        """
        检查许可证是否有效

        :return: 是否有效
        """
        # 检查状态和有效期
        if self.status != 'active':
            return False

        current_time = datetime.now()
        return current_time <= self.expires_at

    def add_device(self) -> bool:
        """
        尝试添加设备

        :return: 是否成功添加设备
        """
        if self.current_devices < self.max_devices:
            self.current_devices += 1
            return True
        return False

    def remove_device(self):
        """
        移除一个设备
        """
        self.current_devices = max(0, self.current_devices - 1)

    def revoke(self):
        """
        撤销许可证
        """
        self.status = 'revoked'

    def extend(self, days: int):
        """
        延长许可证有效期

        :param days: 延长的天数
        """
        if self.is_valid():
            self.expires_at += timedelta(days=days)

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典

        :return: 许可证的字典表示
        """
        license_dict = asdict(self)
        # 将 datetime 转换为 ISO 格式字符串
        license_dict['created_at'] = self.created_at.isoformat()
        license_dict['expires_at'] = self.expires_at.isoformat()
        return license_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'License':
        """
        从字典创建许可证

        :param data: 许可证数据字典
        :return: License 实例
        """
        # 转换时间字符串为 datetime 对象
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)


class LicenseManager:
    """
    许可证管理器，处理许可证的生成、验证和管理
    """

    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        初始化许可证管理器

        :param encryption_key: 加密密钥，为None时自动生成
        """
        # 生成或使用提供的加密密钥
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)

        # 许可证存储
        self._licenses: Dict[str, License] = {}

    def generate_license(self,
                         customer_name: str,
                         product_name: str,
                         valid_days: int = 365,
                         max_devices: int = 1,
                         features: Optional[List[str]] = None,
                         **metadata) -> License:
        """
        生成新的许可证

        :param customer_name: 客户名称
        :param product_name: 产品名称
        :param valid_days: 有效天数
        :param max_devices: 最大设备数
        :param features: 许可证特性
        :param metadata: 额外元数据
        :return: 生成的许可证
        """
        license = License(
            customer_name=customer_name,
            product_name=product_name,
            expires_at=datetime.now() + timedelta(days=valid_days),
            max_devices=max_devices,
            features=features or [],
            metadata=metadata
        )

        # 存储许可证
        self._licenses[license.id] = license

        return license

    def validate_license(self, license_id: str, device_id: Optional[str] = None) -> bool:
        """
        验证许可证

        :param license_id: 许可证ID
        :param device_id: 设备ID
        :return: 是否有效
        """
        license = self._licenses.get(license_id)
        if not license:
            return False

        # 检查许可证有效性
        if not license.is_valid():
            return False

        # 如果提供设备ID，尝试添加设备
        if device_id:
            return license.add_device()

        return True

    def get_license(self, license_id: str) -> Optional[License]:
        """
        获取指定ID的许可证

        :param license_id: 许可证ID
        :return: 许可证对象
        """
        return self._licenses.get(license_id)

    def revoke_license(self, license_id: str):
        """
        撤销指定ID的许可证

        :param license_id: 许可证ID
        """
        license = self._licenses.get(license_id)
        if license:
            license.revoke()

    def encrypt_license(self, license: License) -> str:
        """
        加密许可证

        :param license: 许可证对象
        :return: 加密后的许可证字符串
        """
        license_data = license.to_dict()
        serialized_data = str(license_data).encode()
        encrypted_data = self.cipher_suite.encrypt(serialized_data)
        return base64.b64encode(encrypted_data).decode()

    def decrypt_license(self, encrypted_license: str) -> License:
        """
        解密许可证

        :param encrypted_license: 加密的许可证字符串
        :return: 解密后的许可证对象
        """
        decrypted_data = self.cipher_suite.decrypt(
            base64.b64decode(encrypted_license.encode())
        )
        license_dict = eval(decrypted_data.decode())
        return License.from_dict(license_dict)