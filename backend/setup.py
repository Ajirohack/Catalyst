from setuptools import setup, find_packages

setup(
    name="catalyst_backend",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "PyPDF2>=3.0.1",
        "Pillow>=9.5.0",
        "textblob>=0.17.1",
        "nltk>=3.8.1",
        "websockets>=12.0",
        "httpx>=0.25.2",
        "requests>=2.31.0",
        "aiofiles>=23.2.1",
        "python-dotenv>=1.0.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "loguru>=0.7.2",
        "SQLAlchemy>=2.0.23",
        "aiosqlite>=0.19.0",
        "openai>=1.3.8",
        "anthropic>=0.8.1"
    ],
)
