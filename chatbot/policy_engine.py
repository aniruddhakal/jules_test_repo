import datetime

# Define the cancellation policy threshold in days
ORDER_CANCELLATION_POLICY_DAYS = 10

def is_cancellation_allowed(order_placement_date: datetime.date) -> bool:
    """
    Checks if an order is eligible for cancellation based on its placement date.
    Policy: Order can be cancelled if placed less than ORDER_CANCELLATION_POLICY_DAYS ago.
    """
    if not isinstance(order_placement_date, datetime.date):
        # This could also raise a TypeError, but for robustness in a chatbot context,
        # returning False or logging an error might be preferred.
        # For now, let's assume valid input or handle type checking before calling.
        print(f"Warning: Invalid date type received in policy check: {type(order_placement_date)}")
        return False

    # Calculate the difference between today and the order placement date
    days_since_order_placed = (datetime.date.today() - order_placement_date).days

    # Check if the order is within the allowed cancellation period
    if days_since_order_placed < ORDER_CANCELLATION_POLICY_DAYS:
        return True
    else:
        return False

if __name__ == '__main__':
    # Example Usage (for testing this module directly)
    print("--- Testing Policy Engine: is_cancellation_allowed ---")

    # Test cases
    date_today = datetime.date.today()

    # Case 1: Order placed 5 days ago (should be allowed)
    order_date_5_days_ago = date_today - datetime.timedelta(days=5)
    print(f"Order placed on {order_date_5_days_ago} (5 days ago): Eligible for cancellation? {is_cancellation_allowed(order_date_5_days_ago)}")

    # Case 2: Order placed 9 days ago (should be allowed)
    order_date_9_days_ago = date_today - datetime.timedelta(days=9)
    print(f"Order placed on {order_date_9_days_ago} (9 days ago): Eligible for cancellation? {is_cancellation_allowed(order_date_9_days_ago)}")

    # Case 3: Order placed 10 days ago (should NOT be allowed, as it's not *less than* 10 days)
    order_date_10_days_ago = date_today - datetime.timedelta(days=10)
    print(f"Order placed on {order_date_10_days_ago} (10 days ago): Eligible for cancellation? {is_cancellation_allowed(order_date_10_days_ago)}")

    # Case 4: Order placed 15 days ago (should NOT be allowed)
    order_date_15_days_ago = date_today - datetime.timedelta(days=15)
    print(f"Order placed on {order_date_15_days_ago} (15 days ago): Eligible for cancellation? {is_cancellation_allowed(order_date_15_days_ago)}")

    # Case 5: Order placed today (should be allowed)
    order_date_today = date_today
    print(f"Order placed on {order_date_today} (today): Eligible for cancellation? {is_cancellation_allowed(order_date_today)}")

    # Case 6: Order placed in the future (should ideally not happen, but good to test behavior)
    # Current logic: (today - future_date) will be negative, so (-N < 10) will be True.
    # This implies a future order *is* cancellable by current logic, which is fine.
    order_date_future = date_today + datetime.timedelta(days=5)
    print(f"Order placed on {order_date_future} (in the future): Eligible for cancellation? {is_cancellation_allowed(order_date_future)}")

    # Test with a non-date input (optional, depending on how strictly we want to enforce types here vs. in calling code)
    # print(f"Testing with invalid input type: {is_cancellation_allowed('2023-10-01')}")
    # This would currently print the warning and return False due to the isinstance check.
