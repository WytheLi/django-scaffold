import os


def get_env_or_raise(key, default=None):
    """
        获取环境变量，如果不存在则抛出异常
    :param key: 环境变量名
    :param default: 可选默认值，如果提供则不会抛出异常
    :return: 当环境变量不存在且未提供默认值时
    """
    value = os.environ.get(key, default)

    if value is None:
        raise RuntimeError(
            f'Environment variable "{key}" not found. ' "You must set this variable to run this application."
        )

    return value
