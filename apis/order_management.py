import datetime

# Dummy order data
# We'll use a dictionary to store orders, with order_id as the key.
# This makes lookups by order_id easier.
dummy_orders = {
    "ORD1001": {
        "items": ["Laptop", "Mouse"],
        "status": "shipped",
        "order_date": datetime.date(2023, 10, 20),
        "details": "Shipped via Express Delivery. Tracking ID: XYZ123"
    },
    "ORD1002": {
        "items": ["Keyboard", "Monitor"],
        "status": "processing",
        "order_date": datetime.date(2023, 10, 28),
        "details": "Currently being processed by the warehouse."
    },
    "ORD1003": {
        "items": ["Webcam"],
        "status": "delivered",
        "order_date": datetime.date(2023, 9, 15),
        "details": "Delivered on 2023-09-20."
    },
    "ORD1004": {
        "items": ["USB Hub"],
        "status": "processing",
        "order_date": datetime.date.today() - datetime.timedelta(days=5), # Order placed 5 days ago
        "details": "Awaiting shipment."
    },
    "ORD1005": {
        "items": ["External Hard Drive"],
        "status": "shipped",
        "order_date": datetime.date.today() - datetime.timedelta(days=15), # Order placed 15 days ago
        "details": "Shipped via Standard Delivery. Tracking ID: ABC789"
    }
}

def track_order(order_id: str) -> dict:
    """
    Simulates tracking an order.
    Returns the order details if found, otherwise an error message.
    """
    if order_id in dummy_orders:
        order = dummy_orders[order_id]
        return {
            "status": "success",
            "order_id": order_id,
            "current_status": order["status"],
            "details": order["details"],
            "order_date": order["order_date"].isoformat() # Return date as string
        }
    else:
        return {
            "status": "error",
            "message": f"Order ID '{order_id}' not found."
        }

def cancel_order(order_id: str) -> dict:
    """
    Simulates cancelling an order.
    For now, it just changes the status to 'cancelled' if the order exists
    and is not already 'delivered' or 'cancelled'.
    Policy logic (e.g., based on order_date) will be handled by the policy engine
    before calling this function.
    """
    if order_id in dummy_orders:
        order = dummy_orders[order_id]
        if order["status"] == "delivered":
            return {
                "status": "error",
                "message": f"Order ID '{order_id}' has already been delivered and cannot be cancelled."
            }
        if order["status"] == "cancelled":
            return {
                "status": "error",
                "message": f"Order ID '{order_id}' has already been cancelled."
            }

        # In a real system, you might have more complex status transitions.
        # For simulation, we'll just update the status.
        original_status = order["status"]
        order["status"] = "cancelled"
        order["details"] = f"Order was cancelled by user. Original status: {original_status}"
        return {
            "status": "success",
            "message": f"Order ID '{order_id}' has been cancelled.",
            "order_id": order_id,
            "new_status": "cancelled"
        }
    else:
        return {
            "status": "error",
            "message": f"Order ID '{order_id}' not found."
        }

if __name__ == '__main__':
    # Example Usage (for testing this module directly)
    print("--- Testing Order Tracking ---")
    print(f"Track ORD1001: {track_order('ORD1001')}")
    print(f"Track ORD1002: {track_order('ORD1002')}")
    print(f"Track ORD9999 (not found): {track_order('ORD9999')}")

    print("\n--- Testing Order Cancellation ---")
    # Test cancelling an order that can be cancelled
    print(f"Cancel ORD1002: {cancel_order('ORD1002')}")
    print(f"Track ORD1002 after cancellation: {track_order('ORD1002')}") # Verify status change

    # Test cancelling a delivered order
    print(f"Cancel ORD1003 (delivered): {cancel_order('ORD1003')}")
    print(f"Track ORD1003 after attempting cancellation: {track_order('ORD1003')}")

    # Test cancelling an already cancelled order
    print(f"Cancel ORD1002 again: {cancel_order('ORD1002')}")

    # Test cancelling a non-existent order
    print(f"Cancel ORD8888 (not found): {cancel_order('ORD8888')}")

    # Test cancelling an order relevant for policy check (ORD1004 - 5 days ago)
    print(f"Cancel ORD1004: {cancel_order('ORD1004')}")
    print(f"Track ORD1004 after cancellation: {track_order('ORD1004')}")

    # Test cancelling an order relevant for policy check (ORD1005 - 15 days old)
    # This function itself doesn't check policy, but we'll use it with the policy engine later.
    print(f"Cancel ORD1005: {cancel_order('ORD1005')}")
    print(f"Track ORD1005 after cancellation: {track_order('ORD1005')}")
