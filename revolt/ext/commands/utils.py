from __future__ import annotations

from inspect import Parameter
from typing import Any, Iterable, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from .client import CommandsClient


__all__ = ("evaluate_parameters",)

ClientT = TypeVar("ClientT", bound="CommandsClient")


def evaluate_parameters(parameters: Iterable[Parameter], globals: dict[str, Any]) -> list[Parameter]:
    new_parameters: list[Parameter] = []

    for parameter in parameters:
        if parameter.annotation is not parameter.empty:
            if isinstance(parameter.annotation, str):
                parameter = parameter.replace(annotation=eval(parameter.annotation, globals))

        new_parameters.append(parameter)

    return new_parameters
