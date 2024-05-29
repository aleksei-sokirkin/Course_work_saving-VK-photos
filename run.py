from configuration import config

print(config)
print(config.vk_id.get_secret_value())
print(config.vk_token.get_secret_value())
print(config.yandex_token.get_secret_value())
