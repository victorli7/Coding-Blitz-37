from flask import Blueprint, request

from feature_flags.errors import FlagConflictError, FlagNotFoundError, FlagStoreError
from feature_flags.serialization import (
    evaluation_to_dict,
    flag_from_dict,
    flag_to_dict,
)
from feature_flags.service import FlagService


def create_flags_blueprint(service: FlagService) -> Blueprint:
    flags = Blueprint("flags", __name__)

    @flags.get("/health")
    def health() -> tuple[dict, int]:
        return {"status": "ok"}, 200

    @flags.get("/flags")
    def list_flags() -> tuple[dict, int]:
        try:
            items = [flag_to_dict(flag) for flag in service.list_flags()]
        except FlagStoreError as exc:
            return {"error": str(exc)}, 503
        return {"flags": items}, 200

    @flags.post("/flags")
    def create_flag() -> tuple[dict, int]:
        try:
            flag = flag_from_dict(request.get_json(silent=True))
            created = service.create_flag(flag)
        except ValueError as exc:
            return {"error": str(exc)}, 400
        except FlagConflictError as exc:
            return {"error": str(exc)}, 409
        except FlagStoreError as exc:
            return {"error": str(exc)}, 503
        return flag_to_dict(created), 201

    @flags.get("/flags/<name>")
    def get_flag(name: str) -> tuple[dict, int]:
        try:
            flag = service.get_flag(name)
        except FlagNotFoundError as exc:
            return {"error": str(exc)}, 404
        except FlagStoreError as exc:
            return {"error": str(exc)}, 503
        return flag_to_dict(flag), 200

    @flags.put("/flags/<name>")
    def update_flag(name: str) -> tuple[dict, int]:
        try:
            flag = flag_from_dict(request.get_json(silent=True))
            updated = service.update_flag(name, flag)
        except ValueError as exc:
            return {"error": str(exc)}, 400
        except FlagNotFoundError as exc:
            return {"error": str(exc)}, 404
        except FlagStoreError as exc:
            return {"error": str(exc)}, 503
        return flag_to_dict(updated), 200

    @flags.delete("/flags/<name>")
    def delete_flag(name: str) -> tuple[dict, int]:
        try:
            service.delete_flag(name)
        except FlagNotFoundError as exc:
            return {"error": str(exc)}, 404
        except FlagStoreError as exc:
            return {"error": str(exc)}, 503
        return "", 204

    @flags.get("/flags/<name>/evaluate")
    def evaluate_flag(name: str) -> tuple[dict, int]:
        context = request.args.to_dict()

        try:
            result = service.evaluate_flag(name, context)
        except FlagNotFoundError as exc:
            return {"error": str(exc)}, 404

        return evaluation_to_dict(result), 200

    return flags
