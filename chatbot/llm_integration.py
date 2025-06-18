import re

def get_llm_response(user_query: str) -> dict:
    """
    Simulates an LLM's response by performing basic intent recognition
    and entity extraction from the user query.

    Args:
        user_query: The raw input string from the user.

    Returns:
        A dictionary with 'intent' and 'entities' (e.g., 'order_id').
        Returns {'intent': 'unknown', 'entities': {}} if intent cannot be determined.
    """
    user_query_lower = user_query.lower()

    # Order ID pattern: at least 3 alphanumeric characters OR contains at least one digit.
    order_id_pattern_str = r"\b([a-z0-9]{3,}|[a-z0-9]*\d[a-z0-9]*)\b"

    # Keywords that are NOT order IDs - expanded list
    noise_words = {
        "cancel", "order", "want", "please", "track", "status", "package", "item", "shipment",
        "my", "is", "a", "an", "the", "me", "for", "of", "help", "need", "hello", "hi", "bye",
        "what", "where", "tell", "can", "i", "to", "it", "get", "with", "cust", "abc", "want"
    }

    def extract_order_id(match_obj, id_pattern_first: bool):
        if not match_obj:
            return None

        groups = match_obj.groups()
        candidate = None
        if id_pattern_first: # True if order_id_pattern_str is the first part of the regex
            # Pattern like: order_id_pattern + keyword_pattern -> groups = (order_id_group_from_pattern, keyword_group)
            candidate = groups[0] # The part matched by order_id_pattern_str's capture group
        else: # False if keyword_pattern is first
            # Pattern like: keyword_pattern + order_id_pattern -> groups = (keyword_group, order_id_group_from_pattern) or just (order_id_group_from_pattern)
            if len(groups) == 1: # Only the order_id_pattern_str's capture group was present in the regex
                 candidate = groups[0]
            else: # Keyword pattern also had a capture group, order_id_pattern_str's group is the last one
                 candidate = groups[-1]

        candidate_lower = candidate.lower()
        if candidate and candidate_lower not in noise_words:
            # If purely alpha, require minimum length (e.g., 4 chars) unless it contains digits.
            # The [a-z0-9]{3,} in regex already handles min length 3 for all cases.
            # This is an additional safeguard for purely alpha candidates.
            if candidate.isalpha() and len(candidate) < 4 and not any(char.isdigit() for char in candidate):
                 # Allow short alpha if it's common like 'ORD', 'TRK' - but those usually have numbers.
                 # This rule is tricky. 'CUST' could be part of CUST555.
                 # For now, if it's short AND purely alpha AND in noise_words, it's out.
                 # If it's short AND purely alpha AND NOT in noise_words (e.g. "box"), it might be an ID.
                 # Let's primarily rely on noise_words and the regex's own length/digit requirements.
                 pass # Relying on regex: `[a-z0-9]{3,}` or `[a-z0-9]*\d[a-z0-9]*`

            # Ensure it's not just a substring of a noise word if regex is too loose.
            # (e.g. if order_id_pattern allows "can" from "cancel") - current regex \b boundary handles this.
            return candidate.upper()
        return None

    # --- Intent Recognition and Entity Extraction ---
    intent = "unknown"
    entities = {}

    # Try to find the best generic order ID from all potential matches in the query
    all_potential_ids_matches = re.findall(order_id_pattern_str, user_query_lower)
    found_generic_id = None
    if all_potential_ids_matches:
        best_candidate_so_far = None
        candidate_has_digit = False
        for p_id in all_potential_ids_matches: # re.findall returns list of strings (captured group)
            if p_id.lower() not in noise_words:
                current_has_digit = any(char.isdigit() for char in p_id)
                if not best_candidate_so_far:
                    best_candidate_so_far = p_id
                    candidate_has_digit = current_has_digit
                else:
                    # Prioritize IDs with digits
                    if current_has_digit and not candidate_has_digit:
                        best_candidate_so_far = p_id
                        candidate_has_digit = True
                    elif current_has_digit == candidate_has_digit:
                        # If both have/don't have digits, prefer longer one
                        if len(p_id) > len(best_candidate_so_far):
                            best_candidate_so_far = p_id
                    # If current doesn't have digit and best_candidate_so_far does, keep best_candidate_so_far

        if best_candidate_so_far:
            found_generic_id = best_candidate_so_far.upper()

    # Cancellation Intent
    # Pattern 1: cancel ... <order_id> (keyword not captured, order_id is group 0 of order_id_pattern_str)
    cancel_match1 = re.search(r"cancel.*?" + order_id_pattern_str, user_query_lower, re.IGNORECASE)
    # Pattern 2: <order_id> ... cancel (order_id is group 0 of order_id_pattern_str, keyword not captured)
    cancel_match2 = re.search(order_id_pattern_str + r".*?cancel", user_query_lower, re.IGNORECASE)

    # Tracking Intent
    # Pattern 1: (track|status|where is) ... <order_id> (keyword captured as group 0, order_id is group 1 of combined)
    track_match1 = re.search(r"(track|status|where is).*?" + order_id_pattern_str, user_query_lower, re.IGNORECASE)
    # Pattern 2: <order_id> ... (track|status) (order_id group 0 of order_id_pattern_str, keyword group 1 of combined)
    track_match2 = re.search(order_id_pattern_str + r".*?(track|status)", user_query_lower, re.IGNORECASE)

    extracted_id_for_cancel = None
    if cancel_match1: extracted_id_for_cancel = extract_order_id(cancel_match1, id_pattern_first=False)
    if not extracted_id_for_cancel and cancel_match2: extracted_id_for_cancel = extract_order_id(cancel_match2, id_pattern_first=True)

    extracted_id_for_track = None
    if track_match1: extracted_id_for_track = extract_order_id(track_match1, id_pattern_first=False)
    if not extracted_id_for_track and track_match2: extracted_id_for_track = extract_order_id(track_match2, id_pattern_first=True)

    # Determine intent based on keywords and extracted IDs
    cancel_keywords_present = "cancel" in user_query_lower
    track_keywords_present = any(kw in user_query_lower for kw in ["track", "status", "where is", "where is my order"]) # "where is" is key

    if cancel_keywords_present and track_keywords_present:
        # Ambiguous: "track order X and cancel order Y"
        if extracted_id_for_cancel and extracted_id_for_track and extracted_id_for_cancel != extracted_id_for_track:
            # Truly ambiguous if different IDs are found for different actions. Default to asking user.
            intent = "ambiguous_request" # Or handle by splitting, not supported by this simple model
            entities["cancel_order_id"] = extracted_id_for_cancel
            entities["track_order_id"] = extracted_id_for_track
        elif extracted_id_for_cancel: # If only cancel ID found, or same ID for both
            intent = "cancel_order"
            entities["order_id"] = extracted_id_for_cancel
        elif extracted_id_for_track: # If only track ID found
            intent = "track_order"
            entities["order_id"] = extracted_id_for_track
        else: # No specific IDs, rely on generic or keyword order. Let's default to track as less destructive.
            intent = "track_order"
            if found_generic_id: entities["order_id"] = found_generic_id

    elif cancel_keywords_present:
        intent = "cancel_order"
        if extracted_id_for_cancel: entities["order_id"] = extracted_id_for_cancel
        elif found_generic_id: entities["order_id"] = found_generic_id

    elif track_keywords_present:
        intent = "track_order"
        if extracted_id_for_track: entities["order_id"] = extracted_id_for_track
        elif found_generic_id: entities["order_id"] = found_generic_id

    # Fallback for generic ID if no intent keywords were strongly matched
    if intent == "unknown" and found_generic_id:
        # Could be "ORD123" - what to do? For now, we'll leave intent unknown.
        # A real chatbot might ask "What do you want to do with order ORD123?"
        pass

    # Greeting or simple conversation (can override if no strong order intent or ID)
    if intent == "unknown" or (intent in ["cancel_order", "track_order"] and not entities.get("order_id")):
        if "hello" in user_query_lower or "hi" in user_query_lower:
            intent = "greeting"
        if "bye" in user_query_lower: # "bye" should take precedence over "hello" if both present and no other intent
            intent = "goodbye"
        # If intent was already "cancel/track_order" but no ID, keep that intent.
        if intent in ["cancel_order", "track_order"] and entities.get("order_id"): # ID was found by generic means
             pass # Keep order-related intent
        elif "hello" in user_query_lower or "hi" in user_query_lower: # check again if it was overridden by empty order intent
            intent = "greeting"


    # Final check: if we have an order-related intent but no order_id, the main loop will ask for it.
    # If intent is greeting/goodbye, clear any incidentally picked up order_id.
    if intent in ["greeting", "goodbye", "unknown"] and "order_id" in entities:
        if not (cancel_keywords_present or track_keywords_present): # only clear if no keywords
            del entities["order_id"]

    return {"intent": intent, "entities": entities}

if __name__ == '__main__':
    print("--- Testing Simulated LLM Response Generation ---")
    queries = [
        "Hello there!",
        "Can I cancel my order ORD123?",
        "I want to cancel ORD456 please.",
        "cancel order ABC789",
        "Track my package TRK990",
        "What's the status of my order ORD1001?",
        "Where is my order ITEM007?",
        "I need help with order CUST555, can I cancel it?",
        "Track item XYZ123 and also tell me if I can cancel PQR456", # Ambiguous test
        "I want to track my shipment.", # Missing order ID
        "Need to cancel an order.",    # Missing order ID
        "What can you do?",
        "Thanks, bye!",
        "ORDER CANCEL ORD2000" # Test case sensitivity and word order
    ]

    for query in queries:
        response = get_llm_response(query)
        print(f"Query: \"{query}\" -> Intent: {response['intent']}, Entities: {response['entities']}")

    print("\n--- Specific Edge Cases ---")
    query_edge_cancel_only = "cancel"
    print(f"Query: \"{query_edge_cancel_only}\" -> Intent: {get_llm_response(query_edge_cancel_only)['intent']}, Entities: {get_llm_response(query_edge_cancel_only)['entities']}")

    query_edge_track_only = "track"
    print(f"Query: \"{query_edge_track_only}\" -> Intent: {get_llm_response(query_edge_track_only)['intent']}, Entities: {get_llm_response(query_edge_track_only)['entities']}")

    query_id_only = "ORD123"
    print(f"Query: \"{query_id_only}\" -> Intent: {get_llm_response(query_id_only)['intent']}, Entities: {get_llm_response(query_id_only)['entities']}")

    query_cancel_later = "My order is ORD777, I want to cancel it"
    print(f"Query: \"{query_cancel_later}\" -> Intent: {get_llm_response(query_cancel_later)['intent']}, Entities: {get_llm_response(query_cancel_later)['entities']}")

    query_track_later = "For my order TRK001, can you track it?"
    print(f"Query: \"{query_track_later}\" -> Intent: {get_llm_response(query_track_later)['intent']}, Entities: {get_llm_response(query_track_later)['entities']}")
