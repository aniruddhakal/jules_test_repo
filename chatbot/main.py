import sys
import os
from datetime import datetime, date
import random # For selecting redirection phrases

# Adjust Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from chatbot.llm_integration import get_llm_response, llm as llm_instance
    from chatbot import api_client
    from chatbot.policy_engine import is_cancellation_allowed
except ModuleNotFoundError as e:
    print(f"Error: A required module was not found: {e}")
    sys.exit(1)
except ImportError as e:
    print(f"Error: An import failed: {e}")
    sys.exit(1)

# Redirection phrases
REDIRECTION_PHRASES = [
    "I'm designed to help with questions about your orders. Is there anything about your orders I can assist you with today?",
    "My main purpose is to help you track or cancel orders, or discuss details about them. Do you have any order-related questions?",
    "That's an interesting point! However, I'm best at handling inquiries about your orders. Can I help you with an order?",
    "I can assist with order tracking, cancellations, and other order-specific questions. How can I help you with your orders?"
]

def handle_track_order(entities: dict):
    order_id = entities.get("order_id")
    if not order_id:
        print("Chatbot: I can certainly help you track an order! Could you please provide the order ID?")
        return

    print(f"Chatbot: Okay, tracking order {order_id}...")
    try:
        response = api_client.get_order_status(order_id)
        if response.get("status") == "success":
            print(f"Chatbot: Order {order_id} status: {response.get('current_status')}. Details: {response.get('details')}")
        else:
            print(f"Chatbot: Sorry, I couldn't track that order. {response.get('message', 'No details available.')}")
    except Exception as e:
        print(f"Chatbot: An error occurred while trying to track the order: {e}")

def handle_cancel_order(entities: dict):
    order_id = entities.get("order_id")
    if not order_id:
        print("Chatbot: I can assist with cancelling an order. Could you please provide the order ID?")
        return

    print(f"Chatbot: Attempting to process cancellation for order {order_id}...")
    try:
        order_details_response = api_client.get_order_status(order_id)

        if order_details_response.get("status") != "success":
            print(f"Chatbot: Sorry, I couldn't find order {order_id} to proceed with cancellation. {order_details_response.get('message', '')}")
            return

        current_status = order_details_response.get("current_status")
        if current_status in ["cancelled", "delivered"]:
            print(f"Chatbot: Order {order_id} cannot be cancelled as it is already {current_status}.")
            return

        order_date_str = order_details_response.get("order_date")
        if not order_date_str:
            print(f"Chatbot: Could not retrieve order date for {order_id}. Cannot check cancellation policy.")
            return

        try:
            order_placement_date = date.fromisoformat(order_date_str)
        except ValueError:
            print(f"Chatbot: Invalid date format received for order {order_id}. Cannot check cancellation policy.")
            return

        if not is_cancellation_allowed(order_placement_date):
            print(f"Chatbot: I'm sorry, but order {order_id} cannot be cancelled because it was placed more than 10 days ago according to our policy.")
            return

        print(f"Chatbot: Order {order_id} is eligible for cancellation. Proceeding...")
        cancel_response = api_client.request_order_cancellation(order_id)
        if cancel_response.get("status") == "success":
            print(f"Chatbot: {cancel_response.get('message', f'Order {order_id} has been cancelled.')}")
        else:
            print(f"Chatbot: Could not cancel order {order_id}. Reason: {cancel_response.get('message', 'An error occurred.')}")

    except Exception as e:
        print(f"Chatbot: An error occurred while trying to cancel the order: {e}")

def handle_general_order_query(entities: dict):
    """Handles general questions or discussions about orders."""
    order_id = entities.get("order_id")
    if order_id:
        print(f"Chatbot: I understand you have a query about order {order_id}. Could you please tell me more specifically what you need help with regarding this order, such as tracking its status or an issue with an item?")
    else:
        print("Chatbot: I can help with general questions about your orders. To assist you better, could you please provide an order ID, or tell me more about what you'd like to discuss regarding your orders?")

def run_chatbot():
    if not llm_instance:
        print("Chatbot Critical Error: LLM is not available. Please check your configuration and API keys.")
        print("The chatbot cannot function without an LLM. Exiting.")
        return

    print("Chatbot: Hello! I am your Order Management Assistant. How can I help you today?")
    print("Chatbot: You can ask me to track, cancel, or discuss your order (e.g., 'track ORD123', 'cancel XYZ789', 'tell me about my order ABC111'). Type 'bye' to exit.")

    while True:
        user_query = input("You: ")
        if not user_query.strip():
            continue

        llm_response = get_llm_response(user_query)
        intent = llm_response.get("intent")
        entities = llm_response.get("entities", {})

        # print(f"DEBUG: LLM Response: Intent='{intent}', Entities='{entities}'")

        if intent == "off_topic":
            print(f"Chatbot: {random.choice(REDIRECTION_PHRASES)}")
        elif intent == "greeting":
            print("Chatbot: Hello again! How can I assist with your orders?")
        elif intent == "goodbye":
            print("Chatbot: Goodbye! Have a great day.")
            break
        elif intent == "track_order":
            handle_track_order(entities)
        elif intent == "cancel_order":
            handle_cancel_order(entities)
        elif intent == "general_order_query":
            handle_general_order_query(entities)
        elif intent == "unknown":
            print("Chatbot: I'm sorry, I didn't quite understand that. Could you please rephrase your order-related question?")
        elif intent == "error_llm_unavailable" or intent == "error_llm_processing":
            error_msg = llm_response.get("error_message", "An issue occurred with the language model.")
            print(f"Chatbot: I'm having some technical difficulties at the moment. {error_msg}")
            print("Chatbot: Please try again in a few moments.")
        else:
            print(f"Chatbot: I received an unexpected intent: {intent}. I'll try my best to help if it's order-related, or you can try rephrasing.")

        print("-" * 20)

if __name__ == "__main__":
    print("Starting Chatbot...")
    if 'get_llm_response' not in globals() or \
       'api_client' not in globals() or \
       'is_cancellation_allowed' not in globals():
        print("Chatbot could not start due to missing critical components.")
    else:
        run_chatbot()
