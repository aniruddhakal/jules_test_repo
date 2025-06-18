# Chatbot Test Cases

This document outlines test cases for evaluating the generative chatbot's functionality,
policy adherence, and API integration.

## Orders for Testing:

Refer to `apis/order_management.py` for specific order details. Here's a summary of relevant orders for policy testing:

*   **ORD1001**: Shipped, Order Date: 2023-10-20 (older than 10 days from a test date like 2023-11-05)
*   **ORD1002**: Processing, Order Date: 2023-10-28 (less than 10 days from a test date like 2023-11-05)
*   **ORD1003**: Delivered, Order Date: 2023-09-15 (older than 10 days, and also delivered)
*   **ORD1004**: Processing, Order Date: 5 days ago (relative to current date, should be cancellable)
*   **ORD1005**: Shipped, Order Date: 15 days ago (relative to current date, should NOT be cancellable)
*   **ORD_NON_EXISTENT**: An order ID that does not exist in the system.

*(Note: For date-sensitive tests, the exact outcome for ORD1001, ORD1002, ORD1003 depends on the current date the test is run, unless their dates are also relative. ORD1004 and ORD1005 are always relative to 'today'.)*

---

## Test Case Suite

### TC-001: Successful Order Tracking

*   **User Input:** "Can you track my order ORD1001?"
*   **Expected LLM Output (Simulated):** Intent: `track_order`, Entities: `{'order_id': 'ORD1001'}`
*   **Expected Action:** Call `api_client.get_order_status("ORD1001")`.
*   **Expected API Response (Simulated):** Status: `success`, current_status: `shipped`, details: "Shipped via Express Delivery..."
*   **Expected Chatbot Response:** "Your order ORD1001 has been shipped. Details: Shipped via Express Delivery. Tracking ID: XYZ123"

### TC-002: Order Tracking - Order Not Found

*   **User Input:** "Track order ORD_NON_EXISTENT"
*   **Expected LLM Output (Simulated):** Intent: `track_order`, Entities: `{'order_id': 'ORD_NON_EXISTENT'}`
*   **Expected Action:** Call `api_client.get_order_status("ORD_NON_EXISTENT")`.
*   **Expected API Response (Simulated):** Status: `error`, message: "Order ID 'ORD_NON_EXISTENT' not found."
*   **Expected Chatbot Response:** "Sorry, I couldn't find any information for order ID ORD_NON_EXISTENT."

### TC-003: Successful Order Cancellation (Within Policy)

*   **User Input:** "I need to cancel order ORD1004." (Assuming ORD1004 was placed 5 days ago)
*   **Expected LLM Output (Simulated):** Intent: `cancel_order`, Entities: `{'order_id': 'ORD1004'}`
*   **Expected Action:**
    1.  Call `api_client.get_order_status("ORD1004")` to get order date.
    2.  Call `policy_engine.is_cancellation_allowed(order_date_from_api)`. Expected: `True`.
    3.  Call `api_client.request_order_cancellation("ORD1004")`.
*   **Expected API Response (Cancellation):** Status: `success`, message: "Order ID 'ORD1004' has been cancelled."
*   **Expected Chatbot Response:** "Your order ORD1004 has been successfully cancelled."

### TC-004: Unsuccessful Order Cancellation (Outside Policy - Too Old)

*   **User Input:** "Cancel my order ORD1005." (Assuming ORD1005 was placed 15 days ago)
*   **Expected LLM Output (Simulated):** Intent: `cancel_order`, Entities: `{'order_id': 'ORD1005'}`
*   **Expected Action:**
    1.  Call `api_client.get_order_status("ORD1005")` to get order date.
    2.  Call `policy_engine.is_cancellation_allowed(order_date_from_api)`. Expected: `False`.
*   **Expected Chatbot Response:** "I'm sorry, but order ORD1005 cannot be cancelled as it was placed more than 10 days ago." (Or similar, based on policy)

### TC-005: Unsuccessful Order Cancellation (Order Not Found)

*   **User Input:** "Please cancel ORD_NON_EXISTENT for me."
*   **Expected LLM Output (Simulated):** Intent: `cancel_order`, Entities: `{'order_id': 'ORD_NON_EXISTENT'}`
*   **Expected Action:** Call `api_client.get_order_status("ORD_NON_EXISTENT")` to check existence and get order date.
*   **Expected API Response (Track):** Status: `error`, message: "Order ID 'ORD_NON_EXISTENT' not found."
*   **Expected Chatbot Response:** "Sorry, I couldn't find order ID ORD_NON_EXISTENT to cancel."

### TC-006: Unsuccessful Order Cancellation (Already Delivered)

*   **User Input:** "I want to cancel order ORD1003."
*   **Expected LLM Output (Simulated):** Intent: `cancel_order`, Entities: `{'order_id': 'ORD1003'}`
*   **Expected Action:**
    1.  Call `api_client.get_order_status("ORD1003")`. API returns status 'delivered'.
    2.  (Policy check for date might occur, but the 'delivered' status from API should take precedence for cancellation eligibility by the API itself).
    3.  Attempt `api_client.request_order_cancellation("ORD1003")`.
*   **Expected API Response (Cancellation):** Status: `error`, message: "Order ID 'ORD1003' has already been delivered and cannot be cancelled."
*   **Expected Chatbot Response:** "Order ORD1003 has already been delivered and cannot be cancelled."

### TC-007: Order Tracking - Missing Order ID

*   **User Input:** "Track my order."
*   **Expected LLM Output (Simulated):** Intent: `track_order`, Entities: `{}`
*   **Expected Action:** Chatbot identifies missing order ID.
*   **Expected Chatbot Response:** "Sure, I can help with that. What is your order ID?"

### TC-008: Order Cancellation - Missing Order ID

*   **User Input:** "I want to cancel an order."
*   **Expected LLM Output (Simulated):** Intent: `cancel_order`, Entities: `{}`
*   **Expected Action:** Chatbot identifies missing order ID.
*   **Expected Chatbot Response:** "Okay, I can assist with cancelling an order. Could you please provide the order ID?"

### TC-009: Greeting

*   **User Input:** "Hi"
*   **Expected LLM Output (Simulated):** Intent: `greeting`, Entities: `{}`
*   **Expected Chatbot Response:** "Hello! How can I help you today?" (or similar greeting)

### TC-010: Goodbye

*   **User Input:** "Bye"
*   **Expected LLM Output (Simulated):** Intent: `goodbye`, Entities: `{}`
*   **Expected Chatbot Response:** "Goodbye! Have a great day." (or similar closing)

### TC-011: Ambiguous Query (Order ID only)

*   **User Input:** "ORD1002"
*   **Expected LLM Output (Simulated):** Intent: `unknown` (or a default like `track_order` if an ID is present but no clear verb), Entities: `{'order_id': 'ORD1002'}` or `{}`
*   **Expected Chatbot Response:** "What would you like to do with order ORD1002? You can track it or request to cancel it." (Or ask for clarification)

### TC-012: Order Cancellation (Already Cancelled)
*   **Pre-condition:** ORD1004 has been successfully cancelled in a previous step (e.g., TC-003).
*   **User Input:** "Cancel order ORD1004 again."
*   **Expected LLM Output (Simulated):** Intent: `cancel_order`, Entities: `{'order_id': 'ORD1004'}`
*   **Expected Action:**
    1. Call `api_client.get_order_status("ORD1004")`. API returns status 'cancelled'.
    2. (Policy check might be skipped if status is already terminal like 'cancelled').
    3. Attempt `api_client.request_order_cancellation("ORD1004")`.
*   **Expected API Response (Cancellation):** Status: `error`, message: "Order ID 'ORD1004' has already been cancelled."
*   **Expected Chatbot Response:** "Order ORD1004 has already been cancelled."

---
## Evaluation Notes:

*   **Step-by-step action handling:** Manually verify if the chatbot follows the expected sequence of actions (LLM interpretation, API calls, policy checks).
*   **Response Accuracy:** Does the chatbot provide factually correct information based on API responses and policy?
*   **Policy Adherence:** Does the chatbot correctly enforce defined company policies?
*   **Clarity of Communication:** Is the chatbot's language clear, user-friendly, and helpful?
*   **Error Handling:** How does the chatbot handle unexpected inputs, API errors, or situations not covered by policies?
