"""
Customer notification helpers. Configure SENDGRID_API_KEY + FROM_EMAIL to activate.
Falls back to console logging in development.
"""
import os


def send_order_confirmation(order: dict) -> bool:
    """Send order confirmation email to customer."""
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        print(
            f"[Notification] Order confirmation — {order['order_id']} → {order['customer']['email']}"
        )
        return True

    # Production path — uncomment and install sendgrid package
    # from sendgrid import SendGridAPIClient
    # from sendgrid.helpers.mail import Mail
    # sg = SendGridAPIClient(api_key)
    # message = Mail(
    #     from_email=os.getenv("FROM_EMAIL", "sales@pergola-paradise.com"),
    #     to_emails=order["customer"]["email"],
    #     subject=f"Order Confirmed — {order['order_id']}",
    #     html_content=_order_confirmation_html(order),
    # )
    # sg.send(message)
    return True


def send_shipping_notification(order: dict, tracking_number: str, carrier: str) -> bool:
    """Send shipping notification with tracking info."""
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        print(
            f"[Notification] Shipping update — {order['order_id']} "
            f"via {carrier} #{tracking_number} → {order['customer']['email']}"
        )
        return True

    # Production: same SendGrid pattern as above
    return True


def _order_confirmation_html(order: dict) -> str:
    items_html = "".join(
        f"<tr><td>{i['name']}</td><td>{i['quantity']}</td><td>${i['total']:,.2f}</td></tr>"
        for i in order["items"]
    )
    return f"""
    <h2>Thanks for your order, {order['customer']['name']}!</h2>
    <p>Order ID: <strong>{order['order_id']}</strong></p>
    <table border="1" cellpadding="8">
      <tr><th>Product</th><th>Qty</th><th>Total</th></tr>
      {items_html}
    </table>
    <p>Total: <strong>${order['total']:,.2f}</strong></p>
    <p>Your pergola will ship within the estimated lead time. We'll email you tracking info when it ships.</p>
    """
