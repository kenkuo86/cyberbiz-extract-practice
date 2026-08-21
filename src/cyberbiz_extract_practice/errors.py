# 定義所有錯誤類別

class CyberbizError(Exception):
    pass

class AuthError(CyberbizError):
    pass

class RateLimitError(CyberbizError):
    pass

class ServerError(CyberbizError):
    pass

class SchemaError(CyberbizError):
    pass

class ClientError(CyberbizError):
    pass