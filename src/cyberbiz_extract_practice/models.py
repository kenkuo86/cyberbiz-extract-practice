from dataclasses import dataclass

# dataclass

@dataclass
class Order:
    id: int
    subtotal_price: float
    created_at: str
    updated_at: str
    order_number: int
    order_name: str
    shipping_type: str
    merchant_trade_no: str
    delivery_date: str | None

    @classmethod
    def from_api(cls, raw: dict) -> "Order":
        return cls(
            id=raw["id"],
            subtotal_price=raw["subtotal_price"],
            created_at=raw["created_at"],
            updated_at=raw["updated_at"],
            order_number=raw["order_number"],
            order_name=raw["order_name"],
            shipping_type=raw["shipping_type"],
            merchant_trade_no=raw["merchant_trade_no"],
            delivery_date=raw["delivery_date"]
        )