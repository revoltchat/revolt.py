from inspect import Parameter
from typing import Iterable, Any

__all__ = ("evaluate_parameters",)

def evaluate_parameters(parameters: Iterable[Parameter], globals: dict[str, Any]) -> list[Parameter]:
    new_parameters = []

    for parameter in parameters:
        if parameter.annotation is not parameter.empty:
            if isinstance(parameter.annotation, str):
                parameter = parameter.replace(annotation=eval(parameter.annotation, globals))

        new_parameters.append(parameter)

    return new_parameters
