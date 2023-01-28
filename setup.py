from setuptools import setup, find_packages

setup(
    name='nonebot_plugin_zyk_lightNVL',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/ZYKsslm/nonebot_plugin_zyk_lightNVL',
    license='MIT LICENSE',
    author='ZYKsslm',
    author_email='3119964735@qq.com',
    description='A plugin for nonebot2',
    install_requires=["httpx", "colorama", "lxml", "fake_useragent", "nonebot2", "nonebot_adapter_onebot"],
)
