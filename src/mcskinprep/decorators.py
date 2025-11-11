

from functools import wraps

class OperationName:
    def __init__(self, name):
        self.name = name
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.operation_name = self.name
        return wrapper
    
    @staticmethod
    def get_operation_name(func):
        try:
            return func.operation_name
        except AttributeError:
            return func.__name__
    
    @staticmethod
    def has_operation_name(func):
        return hasattr(func, 'operation_name')


def detectionMethod(method_name):
    """
    decorator: adds detection method attribute to the function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.detection_method = method_name
        return wrapper
    return decorator

def convertMethod(method_name):
    """
    decorator: adds convert method attribute to the function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.convert_method = method_name
        return wrapper
    return decorator