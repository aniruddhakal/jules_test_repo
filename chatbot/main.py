import sys
import os
from datetime import datetime, date

# Adjust Python path to include the project root for sibling module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Chatbot components
try:
    from chatbot.llm_integration import get_llm_response, llm as llm_instance # also import llm to check availability
    from chatbot import api_client
    from chatbot.policy_engine import is_cancellation_allowed
except ModuleNotFoundError as e:
    print(f"Error: A required module was not found. Please ensure all chatbot components are in place: {e}")
    print("Exiting chatbot.")
    sys.exit(1)
except ImportError as e:
    print(f"Error: An import failed. This might be due to issues in the imported modules: {e}")
    print("Exiting chatbot.")
    sys.exit(1)


def handle_track_order(entities: dict):
    """Handles the logic for tracking an order."""
    order_id = entities.get("order_id")
    if not order_id:
        print("Chatbot: I can help with that! What is the order ID you'd like to track?")
        # In a real app, you'd wait for user's next input here.
        # For this CLI version, we'll just ask and move to next turn.
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
    """Handles the logic for cancelling an order."""
    order_id = entities.get("order_id")
    if not order_id:
        print("Chatbot: Sure, I can help with cancelling an order. What is the order ID?")
        return

    print(f"Chatbot: Attempting to cancel order {order_id}...")
    try:
        # 1. Get order details to check status and date for policy
        order_details_response = api_client.get_order_status(order_id)

        if order_details_response.get("status") != "success":
            print(f"Chatbot: Sorry, I couldn't find order {order_id} to cancel. {order_details_response.get('message', '')}")
            return

        current_status = order_details_response.get("current_status")
        if current_status in ["cancelled", "delivered"]:
            print(f"Chatbot: Order {order_id} cannot be cancelled as it is already {current_status}.")
            return

        order_date_str = order_details_response.get("order_date")
        if not order_date_str:
            print(f"Chatbot: Could not retrieve order date for {order_id}. Cannot proceed with cancellation policy check.")
            return

        try:
            # The date from our simulated API is already a date object if called directly,
            # but if it were from a real JSON API, it would be a string.
            # api_client.get_order_status returns it as an ISO string.
            order_placement_date = date.fromisoformat(order_date_str)
        except ValueError:
            print(f"Chatbot: Invalid date format received for order {order_id}. Cannot check cancellation policy.")
            return

        # 2. Check policy
        if not is_cancellation_allowed(order_placement_date):
            print(f"Chatbot: I'm sorry, but order {order_id} cannot be cancelled because it was placed more than 10 days ago.")
            return

        # 3. If policy allows, attempt cancellation
        print(f"Chatbot: Order {order_id} is eligible for cancellation. Proceeding...")
        cancel_response = api_client.request_order_cancellation(order_id)
        if cancel_response.get("status") == "success":
            print(f"Chatbot: {cancel_response.get('message', f'Order {order_id} has been cancelled.')}")
        else:
            print(f"Chatbot: Could not cancel order {order_id}. Reason: {cancel_response.get('message', 'An error occurred.')}")

    except Exception as e:
        print(f"Chatbot: An error occurred while trying to cancel the order: {e}")


def run_chatbot():
    """Main chatbot interaction loop."""
    # Check if LLM is available first
    if not llm_instance: # llm_instance imported from llm_integration
        print("Chatbot Critical Error: LLM is not available. Please check your configuration and API keys.")
        print("The chatbot cannot function without an LLM. Exiting.")
        return

    print("Chatbot: Hello! I am your Order Management Assistant. How can I help you today?")
    print("Chatbot: You can ask me to track or cancel an order (e.g., 'track order ORD123', 'cancel my order XYZ789'). Type 'bye' to exit.")

    while True:
        user_query = input("You: ")
        if not user_query.strip():
            continue

        llm_response = get_llm_response(user_query)
        intent = llm_response.get("intent")
        entities = llm_response.get("entities", {})

        # print(f"DEBUG: LLM Response: Intent='{intent}', Entities='{entities}'") # For debugging

        if intent == "greeting":
            print("Chatbot: Hello again!")
        elif intent == "goodbye":
            print("Chatbot: Goodbye! Have a great day.")
            break
        elif intent == "track_order":
            handle_track_order(entities)
        elif intent == "cancel_order":
            handle_cancel_order(entities)
        elif intent == "unknown":
            print("Chatbot: I'm sorry, I didn't quite understand that. Could you please rephrase?")
            print("Chatbot: You can ask me to 'track order [ID]' or 'cancel order [ID]'.")
        elif intent == "error_llm_unavailable" or intent == "error_llm_processing":
            error_msg = llm_response.get("error_message", "An issue occurred with the language model.")
            print(f"Chatbot: I'm having some technical difficulties at the moment. {error_msg}")
            print("Chatbot: Please try again in a few moments.")
        else: # Should ideally not happen if intents are well-defined
            print(f"Chatbot: I received an unexpected intent: {intent}. I'm not sure how to handle that yet.")

        print("-" * 20) # Separator for readability

if __name__ == "__main__":
    # Perform initial checks or setup if needed
    print("Starting Chatbot...")
    # Check if required modules were imported successfully
    if 'get_llm_response' not in globals() or \
       'api_client' not in globals() or \
       'is_cancellation_allowed' not in globals():
        print("Chatbot could not start due to missing critical components (likely import errors).")
    else:
        run_chatbot()
