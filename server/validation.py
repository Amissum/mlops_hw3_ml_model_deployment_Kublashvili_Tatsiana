from typing import Iterable
import model_pb2

class ValidationError(Exception):
    pass

def features_to_dict(features: Iterable[model_pb2.Feature]) -> dict[str, float]:
    data = {}
    for f in features:
        if f.name in data:
            raise ValidationError(f"Duplicate feature: {f.name}")
        if not f.name:
            raise ValidationError("Empty feature name")
        data[f.name] = float(f.value)
    if not data:
        raise ValidationError("No features provided")
    return data