""" ERROR TYPES USED ACROSS THE APPLICATION """
class EFLError(Exception):
    """Base class for all EFL errors"""
class InputError(EFLError):
    """the user typed something invalid,show a clear messaege"""
class RateUnavailableError(EFLError):
    """NO EXCHANGE RATE could be loaded"""