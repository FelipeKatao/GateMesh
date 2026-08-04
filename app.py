from pathlib import Path

import yaml
from flask import Flask,Blueprint

from GateMonitor.api import Api_GateMesh
from GateMonitor.monitor import Monitor


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config" / "gateway.yml"


def load_config(config_path: Path) -> dict:

    if not config_path.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {config_path}" 
        )

    if not config_path.is_file():
        raise ValueError(
            f"O caminho de configuração não é um arquivo: {config_path}"
        )

    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

    except yaml.YAMLError as exc:
        raise ValueError(
            f"YAML inválido em '{config_path}': {exc}"
        ) from exc

    if not isinstance(config, dict):
        raise ValueError(
            "A configuração deve possuir um objeto YAML na raiz."
        )

    validate_config(config)

    return config


def validate_config(config: dict) -> None:
    """Valida a estrutura mínima da configuração."""

    if "gateway" not in config:
        raise ValueError(
            "Configuração inválida: seção 'gateway' não encontrada."
        )

    if "routes" not in config:
        raise ValueError(
            "Configuração inválida: seção 'routes' não encontrada."
        )

    gateway = config["gateway"]
    routes = config["routes"]

    if not isinstance(gateway, dict):
        raise ValueError("'gateway' deve ser um objeto.")

    if not isinstance(routes, list):
        raise ValueError("'routes' deve ser uma lista.")

    host = gateway.get("host")
    port = gateway.get("port")

    if not host:
        raise ValueError("'gateway.host' é obrigatório.")

    if not isinstance(port, int) or not (1 <= port <= 65535):
        raise ValueError(
            "'gateway.port' deve ser um número entre 1 e 65535."
        )

    for index, route in enumerate(routes):

        if not isinstance(route, dict):
            raise ValueError(
                f"Rota na posição {index} deve ser um objeto."
            )

        required_fields = ("name", "path", "target")

        for field in required_fields:
            if not route.get(field):
                raise ValueError(
                    f"Campo obrigatório ausente na rota {index}: '{field}'."
                )


def create_app() -> Flask:

    config = load_config(CONFIG_FILE)

    app = Flask(__name__)

    app.config["GATEWAY_CONFIG"] = config

    @app.get("/_gateway/health")
    def health():
        return {
            "status": "healthy"
        }

    @app.get("/_gateway/config")
    def gateway_config():
        return {
            "gateway": config["gateway"],
            "routes": config["routes"],
        }

    return app


app = create_app()
app.register_blueprint(Monitor)
app.register_blueprint(Api_GateMesh)

app.secret_key = "gatemesh-monitor-secret-key-change-me"


if __name__ == "__main__":
    config = app.config["GATEWAY_CONFIG"]

    app.run(
        port=config["gateway"]["port"],
        debug=True
    )