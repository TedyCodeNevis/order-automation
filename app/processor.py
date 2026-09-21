from app.logger import setup_logging
from dataclasses import dataclass
from decimal import Decimal,InvalidOperation
from datetime import date as date_gh
from enum import Enum
import logging

setup_logging()
logger=logging.getLogger(__name__)

class statusOrder(str,Enum):
    PROCESSING="processing"
    PENDING="pending"
    COMPLETED="completed"
    SHIPPED="shipped"
    CANCELLED="cancelled"

class InvalidOrderError(Exception):
    """Raised when an order contains invalid data."""

@dataclass
class Order:
    id:int
    customer:str
    customer_email:str
    shipping_address:str
    product:str
    product_id:int
    quantity:int
    total:Decimal
    status:statusOrder
    date:date_gh

REQUIRED_FIELDS=(
    "id",
    "customer",
    "customer_email",
    "shipping_address",
    "product",
    "product_id",
    "quantity",
    "total",
    "status",
    "date",

)

def clean_order(raw_order:dict) -> Order:
    missing=[field for field in REQUIRED_FIELDS if field not in raw_order]
    if missing:
        raise InvalidOrderError(
            f"order {raw_order.get('id','?')} has missing fileds: {missing}"
        )
    try:
        order_id=int(raw_order["id"])
        product_id=int(raw_order["product_id"])
        quantity=int(raw_order["quantity"])
    except(TypeError,ValueError) as error:
        raise InvalidOrderError(
            f"Order{raw_order.get('id','?')} has invalid numeric fields: {error}"
        )
    try:
        total=Decimal(str(raw_order["total"]))
    except(InvalidOperation,ValueError) as error:
        raise InvalidOrderError(
            f"Order {order_id} has invalid total: {raw_order['total']}"
        )
    
    try:
        status=statusOrder(raw_order["status"])
    except ValueError as error:
        raise InvalidOrderError(
            f"Order {order_id} has invalid status: {raw_order['status']}"
        )    
    try:
        order_date=date_gh.fromisoformat(raw_order['date'])
    except(ValueError,TypeError) as error:
        raise InvalidOrderError(
            f"Order {order_id} has invalid date: {raw_order['date']}"
        )
    
    email=raw_order["customer_email"].strip()
    if not email.endswith("@gmail.com"):
        raise InvalidOrderError(f"Order {order_id} has invalid email: {email}")

    if total < 0:
        raise InvalidOrderError(f"Order {order_id} has invalid total: {total}")

    if quantity <=0 :
        raise InvalidOrderError(f"Order {order_id} has invalid quantity field {quantity}")

    return Order(
        id=order_id,
        customer=raw_order["customer"],
        customer_email=email,
        shipping_address=raw_order["shipping_address"],
        product=raw_order["product"],
        product_id=product_id,
        quantity=quantity,
        total=total,
        status=status,
        date=order_date,
    )


def clean_orders(raw_orders:dict) -> list[Order]:
    response_orders=raw_orders.get("orders",[])
    clean_list:list[Order]=[]

    for raw_order in response_orders:
        try:
            order=clean_order(raw_order)
            clean_list.append(order)
        except InvalidOrderError as error:
            logger.warning(f"skipping invalid order : {error}")
            continue

    logger.info(f"Proccessed {len(clean_list)} valid orders out of : {len(response_orders)}")
    return clean_list