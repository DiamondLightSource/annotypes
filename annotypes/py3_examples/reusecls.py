import time

from annotypes import WithCallTypes, add_call_types, Anno
from .simple import Simple

with Anno("Parameters to take"):
    ASimple = Simple


class ReuseCls(WithCallTypes):
    @add_call_types
    def validate(self, params: ASimple) -> ASimple:
        if params.exposure < 0.4:
            params.exposure = 0.4
        return params

    @add_call_types
    def configure(self, params: ASimple):
        time.sleep(params.exposure)



