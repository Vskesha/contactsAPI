from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str = 'contacts'
    postgres_user: str = 'postgres'
    postgres_password: str = '567234'
    postgres_host: str = "localhost"
    sqlalchemy_database_url: str = 'postgresql://postgres:567234@localhost:5432/contacts'
    secret_key: str = 'secret'
    algorithm: str = 'HS256'
    mail_username: str = 'somebody@example.com'
    mail_password: str = 'password'
    mail_from: str = 'somebody@example.com'
    mail_port: int = 1234
    mail_server: str = 'localhost'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str | None = None
    cloudinary_name: str = ''
    cloudinary_api_key: str = ''
    cloudinary_api_secret: str = ''

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
