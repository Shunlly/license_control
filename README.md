# License Manager

## 功能特点

- 生成加密许可证
- 验证许可证有效性
- 支持多设备许可
- 基于时间的许可证到期
- 可自定义许可证特性

## 安装

```bash
pip install license-manager-py
```

## 基本使用

```python
from license_manager.license_control import LicenseManager

# 初始化许可证管理器


key = "mxey3_GNnYDQXsIxK4NABQ0eqmr47coXJLKLkqcdpjU="
lm = LicenseManager(key)
# 生成许可证
license = lm.generate_license()

# 解密许可证
is_valid = lm.decrypt_license("./LICENCE")


# 使用注解的形式，
@lm.validate_license(key, './LICENCE')
def some_function():
    print("License is valid. Function executed.")


some_function()
```

## 许可证管理

- 生成许可证
- 解密许可证
- 验证许可证

## 贡献

欢迎提交PR和Issues！

## 许可证

MIT许可证