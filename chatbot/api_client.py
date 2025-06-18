# Import the simulated API functions.
# We use a relative import assuming 'apis' and 'chatbot' are sibling directories
# or that the project is structured as a package.
# For direct execution or simpler setups, you might need to adjust Python's path
# or use a different import strategy if this causes issues during runtime later.
# For now, let's assume a project structure where this import works.
# If `PYTHONPATH` is set to the project root, this should be fine.
# Example: PYTHONPATH=. python chatbot/main.py (from project root)

try:
    # Attempting import if 'apis' is directly accessible or in PYTHONPATH
    from apis import order_management
except ImportError:
    # Fallback for cases where the structure might be slightly different
    # or when running this file directly for testing without full package setup.
    # This often happens if 'chatbot' is the current working directory.
    import sys
    import os
    # Add the parent directory (project root) to the Python path
    # so that 'apis.order_management' can be found.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from apis import order_management

def get_order_status(order_id: str) -> dict:
    """
    Calls the simulated order tracking API.
    """
    # In a real scenario, this would involve HTTP requests, error handling, etc.
    # Here, we directly call the Python function from the simulated API.
    response = order_management.track_order(order_id)
    return response

def request_order_cancellation(order_id: str) -> dict:
    """
    Calls the simulated order cancellation API.
    Note: This client function itself does not check policy.
    Policy checking should be done by the chatbot logic *before* calling this.
    """
    response = order_management.cancel_order(order_id)
    return response

if __name__ == '__main__':
    # Example Usage (for testing this module directly)
    # This requires the `apis` module to be importable.
    # Ensure your PYTHONPATH is set up correctly if running this directly,
    # e.g., by running from the project's root directory:
    # python -m chatbot.api_client

    print("--- Testing API Client ---")

    # Test Order Tracking
    print("\n--- Testing Order Tracking via API Client ---")
    order_id_track_exists = "ORD1001"
    order_id_track_not_exists = "ORD9999"

    print(f"Tracking order {order_id_track_exists}: {get_order_status(order_id_track_exists)}")
    # Expected: {'status': 'success', 'order_id': 'ORD1001', 'current_status': 'shipped', ...}

    print(f"Tracking order {order_id_track_not_exists}: {get_order_status(order_id_track_not_exists)}")
    # Expected: {'status': 'error', 'message': "Order ID 'ORD9999' not found."}

    # Test Order Cancellation
    print("\n--- Testing Order Cancellation via API Client ---")
    order_id_cancel_processing = "ORD1004" # Assumed to be 'processing' and cancellable by API
    order_id_cancel_delivered = "ORD1003" # Assumed to be 'delivered'
    order_id_cancel_not_exists = "ORD8888"

    # First, let's check initial status of ORD1004 (should be processing)
    # Note: dummy_orders in order_management is modified in-memory by cancel_order.
    # For repeatable tests, it would be better to re-initialize or deepcopy data,
    # but for this simulation, we'll proceed.
    print(f"Initial status of {order_id_cancel_processing}: {get_order_status(order_id_cancel_processing)}")

    print(f"Requesting cancellation for {order_id_cancel_processing}: {request_order_cancellation(order_id_cancel_processing)}")
    # Expected: {'status': 'success', 'message': "Order ID 'ORD1004' has been cancelled.", ...}
    print(f"Status of {order_id_cancel_processing} after cancellation request: {get_order_status(order_id_cancel_processing)}")
    # Expected: current_status should be 'cancelled'

    print(f"Requesting cancellation for {order_id_cancel_delivered}: {request_order_cancellation(order_id_cancel_delivered)}")
    # Expected: {'status': 'error', 'message': "Order ID 'ORD1003' has already been delivered..."}

    print(f"Requesting cancellation for {order_id_cancel_not_exists}: {request_order_cancellation(order_id_cancel_not_exists)}")
    # Expected: {'status': 'error', 'message': "Order ID 'ORD8888' not found."}

    # Reset an order for further testing if needed, or be mindful of state changes.
    # For example, to make ORD1004 'processing' again for other tests:
    # from apis.order_management import dummy_orders
    # if "ORD1004" in dummy_orders:
    # dummy_orders["ORD1004"]["status"] = "processing"
    # dummy_orders["ORD1004"]["details"] = "Awaiting shipment."
    # print(f"Status of {order_id_cancel_processing} after reset: {get_order_status(order_id_cancel_processing)}")
