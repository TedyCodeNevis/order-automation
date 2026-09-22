from processor import Order,OrderStatus

STATUS_EMOJI={
    OrderStatus.PROCESSING:"🕐",
    OrderStatus.PENDING:"⌛",
    OrderStatus.COMPLETED:"✅",
    OrderStatus.SHIPPED:"🚚",
    OrderStatus.CANCELLED:"🚫",
}

STATUS_LABEL={
    OrderStatus.PROCESSING:"در حال پردازش",
    OrderStatus.PENDING:"در انتضار",
    OrderStatus.COMPLETED:"تکمیل شده",
    OrderStatus.SHIPPED:"ارسال شده",
    OrderStatus.CANCELLED:"لغو شده",
}

def format_order(order:Order) -> str:
    """تبدیل جزئیات سفارش به متن قابل خواندن"""
    if not order:
        return "سفارشی وجود ندارد" 
    emoji=STATUS_EMOJI.get(order.status,"📦")
    order_label=STATUS_LABEL.get(order.status,order.status.value)

    return (
        f"{emoji}شماره سفارش  : {order.id}\n"
        f"مشتری: {order.customer}\n"
        f"ایمیل مشتری: {order.customer_email}\n"
        f"محصول: {order.product} (تعداد: {order.quantity})\n"
        f"مجموع قیمت: {order.total:,.2f}\n"
        f"وضعیت: {order_label}\n",
        f"تاریخ سفارش: {order.date.isoformat()}\n",
        f"آدرس: {order.shipping_address}\n",
    )

def format_orders_summary(orders:list[Order]) -> str:
    """خلاصه سازی چند سفارش به صورت یک لیست کوتاه"""

    if not orders:
        return "سفارشی برای نمایش وجود ندارد"
    order_list=[f"📋 {len(orders)} سفارش یافت شد : \n"]
    for order in orders:
        order_list.append(
            f"#{order.id} - {order.customer} - "
            f"{order.product} * {order.quantity} - "
            f"{order.total:,.2f} - {STATUS_LABel.get(order.status,order.status.value)}"
        )
    return "\n".join(order_list)

def format_orders_full(orders:list[Order]) -> str:
    """جزئیات کامل چند سفاذش را بر می گرداند"""

    if not orders:
        return "سفارشی برای نمایش وجد ندارد"

    seperator="\n"+("-" * 30) + "\n"
    return seperator.join(format_order(order) for order in orders)

def format_order_dict(order:Order) -> dict:
    """تبدیل سفارش ها به دیکشنری"""    

    return{
        "id" : order.id,
        "customer" : order.customer,
        "customer_email" : order.customer_email,
        "shipping_address" : order.shipping_address,
        "product" : order.product,
        "product_id" : order.product_id,
        "quantity" : order.quantity,
        "total" : str(order.total),
        "status" : order.status.value,
        "date" : order.date.isoformat(),
    }
    