# 定義所有錯誤類別

class Error:
    pass

class CyberbizError(Error):
    error: str

class AuthError(CyberbizError):
    pass

class RateLimitError(CyberbizError):
    pass

class ServerError(CyberbizError):
    pass

class SchemaError(CyberbizError):
    pass