"""
test_chatbot.py
================
Simple test script to evaluate the FAQ Chatbot matching logic
across 5 sample questions (including in-domain queries and out-of-domain fallback).
"""

from chatbot import get_chatbot_response, SIMILARITY_THRESHOLD


def run_tests():
    sample_queries = [
        "Where is my package tracking?",
        "Can I pay using PayPal or credit card?",
        "How many days do I have to return an item?",
        "When is your support team available?",
        "What is the weather like in New York?"
    ]

    print("=" * 70)
    print("      FAQ CHATBOT TEST SUITE (TF-IDF & COSINE SIMILARITY)")
    print(f"      Similarity Threshold: {SIMILARITY_THRESHOLD}")
    print("=" * 70)

    for idx, query in enumerate(sample_queries, start=1):
        print(f"\n[Test Case {idx}]")
        print(f"User Input       : \"{query}\"")
        
        response = get_chatbot_response(query)
        matched_q = response.get("matched_question")
        confidence = response.get("confidence", 0.0)
        answer = response.get("answer", "")

        print(f"Matched FAQ      : {matched_q if matched_q else 'None (Triggered Fallback)'}")
        print(f"Confidence Score : {confidence} ({int(confidence * 100)}%)")
        print(f"Bot Response     : \"{answer}\"")

        # Basic assertion check for test reporting
        if idx <= 4:
            if matched_q is not None and confidence >= SIMILARITY_THRESHOLD:
                print("Status           : [PASS] Successfully matched relevant FAQ.")
            else:
                print("Status           : [WARN] Expected match but fell back.")
        else:
            if matched_q is None and confidence < SIMILARITY_THRESHOLD:
                print("Status           : [PASS] Successfully caught out-of-domain query with fallback.")
            else:
                print("Status           : [WARN] Expected fallback for out-of-domain query.")

    print("\n" + "=" * 70)
    print("All test queries executed.")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
