from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 32+ bytes to satisfy RFC 7518's HMAC-SHA256 key-length recommendation even
    # in dev — still a placeholder, override via .env for any real deployment.
    jwt_secret: str = "change-me-in-dot-env-this-is-a-dev-only-placeholder"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documents"
    ollama_api_key: str = ""
    # qwen3.5:cloud (and several other large :cloud models) require a paid
    # Ollama subscription — gpt-oss:20b-cloud is confirmed working on the free
    # tier as of this writing. Override via OLLAMA_MODEL once you know your
    # account's actual entitlements (ollama.com/upgrade).
    ollama_model: str = "gpt-oss:20b-cloud"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    # Minimum cosine similarity for a retrieved chunk to count as relevant.
    # Without this, Qdrant's top-k search returns the k nearest neighbors
    # regardless of how weak the match is — once a tenant has any indexed
    # chunks, unrelated ones would otherwise pad out the result set instead
    # of correctly reporting "nothing relevant found".
    retrieval_score_threshold: float = 0.35

    document_storage_path: str = "./data/documents"
    # Users, document metadata, and the audit log all live here — a plain
    # in-memory dict doesn't survive a process restart (which `--reload`
    # triggers on every code change), so anything meant to look like a real
    # app needs this on disk from the start.
    database_path: str = "./data/app.db"

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    # Used to build the link inside password-reset emails.
    frontend_base_url: str = "http://localhost:5173"


settings = Settings()
