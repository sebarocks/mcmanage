from pydantic_settings import BaseSettings, SettingsConfigDict

class MySettings(BaseSettings):
    
    pb_enabled : bool
    activity_check_enabled : bool

    model_config = SettingsConfigDict(env_file='.env',extra='allow')


my_settings = MySettings()