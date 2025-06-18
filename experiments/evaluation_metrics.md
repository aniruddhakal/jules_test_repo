# Chatbot Evaluation Metrics

This document outlines the quantitative and qualitative metrics for evaluating the performance,
effectiveness, and decision-making process of the generative chatbot.

## I. Quantitative Metrics

These metrics provide measurable, numerical insights into the chatbot's performance.

### 1. Task Completion Rate (TCR)
*   **Definition:** The percentage of user requests that were successfully and completely handled by the chatbot.
*   **Formula:** `(Number of Successfully Completed Tasks / Total Number of Task Attempts) * 100%`
*   **How to Measure:** Requires a predefined set of test tasks (e.g., from `test_cases.md`). Each task attempt is manually or semi-automatically labeled as success or failure.
    *   *Success Example (Track):* User asks to track, provides ID, chatbot gives correct status.
    *   *Success Example (Cancel):* User asks to cancel, provides ID, chatbot correctly applies policy and confirms cancellation if eligible.
    *   *Failure Example:* Chatbot misunderstands intent, cannot find a valid order, incorrectly applies policy.

### 2. Intent Recognition Accuracy
*   **Definition:** The percentage of user intents correctly identified by the LLM.
*   **Formula:** `(Number of Correctly Identified Intents / Total Number of User Utterances with Clear Intent) * 100%`
*   **How to Measure:** Requires a labeled dataset of user utterances, each mapped to its ground truth intent. Compare LLM's predicted intent with the ground truth.

### 3. Entity Extraction Accuracy (for `order_id`)
*   **Definition:** The percentage of `order_id`s correctly extracted by the LLM when an order ID is present in the user query and relevant to the intent.
*   **Formula:** `(Number of Correctly Extracted Order_IDs / Total Number of Utterances with Order_IDs to be Extracted) * 100%`
*   **How to Measure:** Requires a labeled dataset where utterances containing order IDs are marked with the correct ID. Compare LLM's extracted `order_id` with the ground truth.

### 4. Policy Adherence Rate
*   **Definition:** The percentage of order cancellation requests that are handled strictly according to the defined company cancellation policy (e.g., 10-day rule).
*   **Formula:** `(Number of Cancellations Handled Correctly per Policy / Total Number of Cancellation Attempts Subject to Policy) * 100%`
*   **How to Measure:** Test with scenarios where orders are within and outside the cancellation window. Verify if the chatbot allows/denies cancellation appropriately.

### 5. Redirection Effectiveness
*   **Definition:** The percentage of off-topic user queries that are correctly identified as 'off_topic' by the LLM and result in a redirection message from the chatbot.
*   **Formula:** `(Number of Off-Topic Queries Correctly Redirected / Total Number of Off-Topic Queries) * 100%`
*   **How to Measure:** Test with a set of clearly off-topic queries. Check if the LLM intent is 'off_topic' and if the chatbot provides a redirection phrase.

### 6. Average Turns per Task (Conversation Length)
*   **Definition:** The average number of conversational turns (one user utterance + one chatbot response = 1 turn) required to complete a specific task.
*   **Formula:** `Sum of Turns for All Completed Tasks / Number of Successfully Completed Tasks`
*   **How to Measure:** For each successfully completed task in a test set, count the number of turns. Lower numbers generally indicate efficiency, but not at the expense of clarity or user experience.

### 7. Error Rate
*   **Definition:** The frequency with which the chatbot makes errors. This can be a broad metric encompassing several types of errors.
*   **Types of Errors:**
    *   *Misinterpretation:* Incorrect intent or entity extraction.
    *   *Incorrect Information:* Providing wrong order status, wrong policy explanation.
    *   *Failed API Calls:* Errors in interacting with backend systems (simulated or real).
    *   *Unhandled Exceptions:* Software crashes or ungraceful error messages.
*   **How to Measure:** `(Total Number of Errors Observed / Total Number of Interactions or Tasks) * 100%`. Requires careful logging and manual review of interactions.

## II. Qualitative Metrics

These metrics capture subjective aspects of the user experience and chatbot performance, often gathered through human evaluation or user feedback.

### 1. User Satisfaction
*   **Definition:** Overall satisfaction of the user with their interaction with the chatbot.
*   **How to Measure:**
    *   **CSAT (Customer Satisfaction Score):** Ask users to rate their satisfaction on a scale (e.g., 1-5) after an interaction.
    *   **SEQ (Single Ease Question):** Ask users "How easy was it to interact with the chatbot?" on a scale (e.g., 1-7, very difficult to very easy).
    *   Open-ended feedback (e.g., "What did you like/dislike?").

### 2. Response Appropriateness & Helpfulness
*   **Definition:** The degree to which the chatbot's responses are contextually relevant, accurate, and useful in addressing the user's query.
*   **How to Measure:** Human evaluators rate responses on a Likert scale (e.g., 1-5 for appropriateness, 1-5 for helpfulness) based on conversation transcripts.

### 3. Conversational Flow & Naturalness
*   **Definition:** How natural, smooth, and human-like the conversation with the chatbot feels.
*   **How to Measure:** Human evaluators rate the conversation on aspects like:
    *   Does the chatbot understand conversational context?
    *   Are transitions between topics smooth?
    *   Is the language used natural or overly robotic?
    *   Does it handle interruptions or clarifications well?

### 4. Clarity of Instructions & Prompts
*   **Definition:** How clear the chatbot is when asking for information or providing instructions to the user.
*   **How to Measure:** Human evaluators assess if the chatbot's questions (e.g., "What is your order ID?") are easy to understand and unambiguous.

### 5. Effectiveness of Redirection (Qualitative Aspect)
*   **Definition:** How gracefully and effectively the chatbot redirects users from off-topic queries without causing frustration.
*   **How to Measure:** Human evaluators assess:
    *   Is the redirection polite?
    *   Is it clear why the chatbot is redirecting?
    *   Does the user seem to accept the redirection or try to push the off-topic subject?

## III. Evaluating the Decision-Making Process

This involves a deeper dive into how the chatbot arrives at its responses and actions. It's more about understanding the internal workings than just the final outcome.

### Methods:
1.  **Log Analysis:**
    *   Review detailed logs of interactions, including:
        *   Raw user query.
        *   LLM's processed input (the prompt).
        *   LLM's raw output.
        *   Parsed intent and entities from the LLM.
        *   API calls made (request and response).
        *   Policy engine checks performed (input and output).
        *   Final chatbot response.
    *   This helps trace the step-by_step handling of a query and identify where errors or misjudgments occur.

2.  **Manual Review of Conversation Transcripts:**
    *   For a set of diverse test cases (including complex or edge cases), manually walk through the conversation.
    *   Compare the chatbot's actions at each step against the expected behavior defined in `test_cases.md` or by expert judgment.
    *   Identify any logical flaws or deviations in the decision-making process.

3.  **"Explainability" (if LLM supports it):**
    *   Some advanced LLM interaction techniques might involve asking the LLM to "explain its reasoning" for a particular intent classification or entity extraction. This can provide insights but needs careful prompt engineering.

By combining these quantitative, qualitative, and decision-making process evaluation methods, a comprehensive understanding of the chatbot's effectiveness and accuracy can be achieved.
