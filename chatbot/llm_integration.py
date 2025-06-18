import sys
import os

# Adjust sys.path to allow direct execution and importing from 'chatbot' package
current_script_path = os.path.abspath(__file__)
chatbot_dir = os.path.dirname(current_script_path)
project_root = os.path.dirname(chatbot_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import json
from chatbot.llm_manager import get_llm
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional, Dict

# Define the desired output structure for the LLM using Pydantic
class LLMResponseFormat(BaseModel):
    intent: str = Field(description=(
        "The user's intent. Must be one of: 'track_order', 'cancel_order', "
        "'general_order_query', 'greeting', 'goodbye', 'off_topic', 'unknown'."
    ))
    entities: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description=(
            "Extracted entities. For 'track_order', 'cancel_order', or 'general_order_query', "
            "should include 'order_id' if found by the LLM."
        )
    )
    # raw_llm_response: Optional[str] = Field(default="", description="The raw text response from the LLM, for debugging.") # Optional

# Global LLM instance and parser
llm = None
parser = None

def initialize_llm_and_parser():
    global llm, parser
    if llm is None:
        llm = get_llm()
        if llm:
            parser = JsonOutputParser(pydantic_object=LLMResponseFormat)
        else:
            parser = None

initialize_llm_and_parser()

def get_llm_response(user_query: str) -> dict:
    """
    Processes the user query using an LLM to determine intent and extract entities.
    Now also identifies 'general_order_query' and 'off_topic' intents.
    """
    global llm, parser

    if not llm or not parser:
        print("LLM Integration Error: LLM or Parser not initialized. Check LLM configuration and API keys.")
        return {"intent": "error_llm_unavailable", "entities": {}, "error_message": "LLM is not available."}

    system_prompt_text = ("""
    You are an AI assistant for an e-commerce chatbot. Your primary goal is to help users with their orders.
    Analyze the user's query to determine their intent and extract relevant entities.

    Possible intents are:
    - 'track_order': User wants to know the status or location of their order.
    - 'cancel_order': User wants to cancel an existing order.
    - 'general_order_query': User has a general question or wants to discuss something about their order(s) that isn't specific tracking or cancellation (e.g., "tell me about my order", "I have an issue with an item in ORD123").
    - 'greeting': User is saying hello or starting a conversation.
    - 'goodbye': User is ending the conversation.
    - 'off_topic': User's query is clearly NOT related to e-commerce orders, their account, shipping, etc. (e.g., asking about weather, jokes, general knowledge).
    - 'unknown': User's query is too vague, ambiguous, or you cannot confidently determine any other intent.

    Entity Extraction:
    - If the intent is 'track_order', 'cancel_order', or 'general_order_query', you MUST try to extract an 'order_id'.
    - An order ID is typically a mix of letters and numbers (e.g., ORD123, ITEMXYZ, 98765ABC).
    - If no specific order ID is mentioned for an order-related intent, do not invent one; return an empty entities dictionary or omit 'order_id'.
    """)

    human_prompt_text = "{format_instructions}\n\nUser Query:\n{query}"

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt_text),
        HumanMessagePromptTemplate.from_template(human_prompt_text)
    ])

    chain = prompt | llm | parser

    try:
        format_instructions = parser.get_format_instructions()
        # print(f"DEBUG: Format Instructions for LLM: {format_instructions}")

        response_data = chain.invoke({
            "query": user_query,
            "format_instructions": format_instructions
        })

        if 'entities' not in response_data or response_data['entities'] is None:
            response_data['entities'] = {}

        return response_data

    except Exception as e:
        print(f"LLM Integration Error: Could not process query due to: {e}")
        return {"intent": "error_llm_processing", "entities": {}, "error_message": str(e)}


if __name__ == '__main__':
    # The sys.path manipulation is already at the top of the file.
    # Re-initialize after path adjustment if llm was None due to import error initially
    # This check is useful if the module was imported by another script that didn't set up path,
    # then this script is run directly.
    if llm is None: # If initial attempt in global scope failed (e.g. if this module was imported before path was set)
        print("LLM was None, attempting re-initialization for direct script run...")
        # We need to re-import get_llm if the initial import failed due to path issues solved just now.
        # However, the path issue is for 'from chatbot.llm_manager', not get_llm itself.
        # The get_llm() in global scope should have worked if chatbot.llm_manager was found due to top-level sys.path.
        # This re-initialization is more of a safeguard or for complex import scenarios.
        initialize_llm_and_parser()


    print("--- Testing LLM Integration (with Topic Management) ---")
    if not llm:
        print("LLM not available (check config.yaml, API keys, and llm_manager.py). Skipping tests.")
    else:
        print(f"Using LLM: {type(llm)}")
        queries = [
            "Hello there!",
            "Can I cancel my order ORD123?",
            "Track my package TRK990",
            "What's the status of my order ORD1001?",
            "I have a question about order CUST555.", # general_order_query
            "Tell me more about ORD777.",             # general_order_query
            "What's the weather like today?",          # off_topic
            "Can you tell me a joke?",                 # off_topic
            "I want to track my shipment.",
            "Need to cancel an order.",
            "What can you do?", # Should be 'unknown' or perhaps 'general_order_query' if LLM is generous
            "Thanks, bye!",
            "My order ORD2000 has an issue with one of the items.", # general_order_query
            "Is my package ORD111 going to be late?" # general_order_query or track_order
        ]

        for query in queries:
            response = get_llm_response(query)
            print(f"Query: \"{query}\" -> Response: {json.dumps(response)}") # Use json.dumps for cleaner dict printing

        print("\n--- Specific Edge Cases ---")
        edge_cases = [
            "cancel",
            "track",
            "ORD123",
            "My order is ORD777, I want to cancel it",
            "The sky is blue.", # off_topic
            "Help me with my order." # general_order_query
        ]
        for query in edge_cases:
            response = get_llm_response(query)
            print(f"Query: \"{query}\" -> Response: {json.dumps(response)}")
