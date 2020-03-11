"""Constant parameter definitions"""

DEFAULT_CONFIG_PATH = "/etc/keyosk/conf.toml"

ENV_CONFIG_PATH = "KYSK_CONF_PATH"

REGEX_FRIENDLY_NAME = r"^([a-z0-9]+)(-[a-z0-9]+)*$"

REGEX_DOMAIN_NAME = REGEX_FRIENDLY_NAME

REGEX_DOMAIN_ACCESS_LIST_NAME = REGEX_FRIENDLY_NAME

REGEX_DOMAIN_PERMISSION_NAME = REGEX_FRIENDLY_NAME

REGEX_DOMAIN_AUDIENCE = r"^[a-z][a-z0-9]{2,9}$"

REGEX_DOMAIN_TITLE = r"^.{1,30}$"
