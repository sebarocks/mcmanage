from pydantic_settings import BaseSettings, SettingsConfigDict

class MySettings(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env',extra='allow')


my_settings = MySettings()