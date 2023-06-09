from enum import Enum

class DevPhase(Enum):
    UNDERSTAND = 1
    ARCHITECTURE = 2
    STRUCTURE_CODE = 3
    STRUCTURE_TESTS = 4
    FLESH_OUT_CODE = 5
    FLESH_OUT_TESTS = 6
    DEPLOY = 7
    IMPROVE = 8

class InferenceStep(Enum):
    IDEATE = 1
    CRITIQUE = 2
    RESOLVE = 3
