"""
chatbot.py
==========
Core NLP module for the FAQ Chatbot.

This module handles:
1. Downloading required NLTK resources automatically on first run.
2. Text preprocessing (lowercasing, punctuation removal, tokenization, stopword removal, lemmatization).
3. TF-IDF vectorization of FAQ questions.
4. Cosine similarity matching to find the most relevant FAQ for user queries.
5. Fallback response mechanism when confidence is below a defined threshold.
"""

import os
import json
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
# If the cosine similarity score is below this threshold,
# the bot treats the question as unmatched and returns a fallback message.
SIMILARITY_THRESHOLD = 0.3

# Friendly fallback response when no FAQ matches with sufficient confidence
FALLBACK_RESPONSE = (
    "Sorry, I couldn't find an answer to that in my knowledge base. "
    "Try rephrasing your question, or ask about shipping, returns, payments, or support!"
)

# Current script directory to locate faqs.json reliably
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAQS_FILE_PATH = os.path.join(BASE_DIR, "faqs.json")


# ==========================================
# NLTK RESOURCE INITIALIZATION
# ==========================================
def ensure_nltk_resources():
    """
    Ensures that required NLTK packages (tokenizers, stopwords, lemmatizer data)
    are downloaded locally before processing any text.
    """
    packages = ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]
    for package in packages:
        try:
            nltk.download(package, quiet=True)
        except Exception as e:
            print(f"[Warning] Could not verify NLTK package '{package}': {e}")


# Run the resource check once when the module loads
ensure_nltk_resources()

# Initialize text processing tools
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


# ==========================================
# TEXT PREPROCESSING PIPELINE
# ==========================================
def preprocess_text(text: str) -> str:
    """
    Standardizes and cleans text through 5 NLP preprocessing steps:
    
    Step 1: Lowercase all characters so 'Shipping' and 'shipping' match.
    Step 2: Remove punctuation characters like '?', '!', and commas.
    Step 3: Tokenize the text into individual words.
    Step 4: Remove stopwords (frequent filler words like 'is', 'the', 'at').
    Step 5: Lemmatize words to their root forms (both verbs & nouns, e.g. 'tracking' -> 'track', 'items' -> 'item').
    
    Returns:
        A cleaned, space-separated string of root words ready for TF-IDF.
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Lowercase
    text = text.lower()

    # 2. Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # 3. Tokenize into words
    tokens = word_tokenize(text)

    # 4 & 5. Filter stopwords and lemmatize to base dictionary form (verbs + nouns)
    clean_tokens = []
    for token in tokens:
        token = token.strip()
        if token and token not in stop_words:
            # Lemmatize both verb forms (e.g., 'tracking' -> 'track') and noun forms (e.g., 'items' -> 'item')
            root_word = lemmatizer.lemmatize(lemmatizer.lemmatize(token, pos="v"), pos="n")
            clean_tokens.append(root_word)

    return " ".join(clean_tokens)


# ==========================================
# FAQ CHATBOT ENGINE CLASS
# ==========================================
class FAQChatbot:
    """
    Manages FAQ loading, TF-IDF model training, and cosine similarity lookup.
    """

    def __init__(self, faqs_path: str = FAQS_FILE_PATH):
        self.faqs_path = faqs_path
        self.faqs = []
        self.raw_questions = []
        self.cleaned_questions = []
        self.vectorizer = None
        self.faq_matrix = None

        # Load data and fit the vectorizer
        self.load_faqs()
        self.train_model()

    def load_faqs(self):
        """
        Loads the list of FAQs from faqs.json.
        """
        if not os.path.exists(self.faqs_path):
            raise FileNotFoundError(f"FAQ file not found at: {self.faqs_path}")

        with open(self.faqs_path, "r", encoding="utf-8") as f:
            self.faqs = json.load(f)

        self.raw_questions = [item["question"] for item in self.faqs]
        print(f"[FAQChatbot] Successfully loaded {len(self.faqs)} FAQs from {os.path.basename(self.faqs_path)}.")

    def train_model(self):
        """
        Preprocesses FAQ questions once and fits the TF-IDF Vectorizer.
        
        WHAT IS TF-IDF?
        - TF (Term Frequency): Measures how frequently a word appears in a specific question.
        - IDF (Inverse Document Frequency): Down-weights common words across all questions
          and highlights rare, informative keywords (e.g. 'refund', 'tracking', 'warranty').
        - The result is a numerical matrix where each question is represented as a vector.
        """
        # Preprocess all FAQ questions once at startup
        self.cleaned_questions = [preprocess_text(q) for q in self.raw_questions]

        # Initialize the TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer()

        # Fit on preprocessed questions and transform them into TF-IDF vectors
        self.faq_matrix = self.vectorizer.fit_transform(self.cleaned_questions)
        print("[FAQChatbot] TF-IDF matrix fitted successfully.")

    def get_response(self, user_question: str) -> dict:
        """
        Finds the most relevant FAQ using TF-IDF and Cosine Similarity.
        
        WHAT IS COSINE SIMILARITY?
        - Measures the angle between two multi-dimensional numerical vectors.
        - Value ranges from 0.0 (completely dissimilar / orthogonal) to 1.0 (exact match).
        - Formula: cos(theta) = (A . B) / (||A|| * ||B||)
        
        Returns:
            dict containing:
            - "answer": str
            - "matched_question": str or None
            - "confidence": float (rounded to 2 decimal places)
        """
        # Handle empty or blank inputs
        if not user_question or not user_question.strip():
            return {
                "answer": "Please ask a question so I can help you!",
                "matched_question": None,
                "confidence": 0.0
            }

        # Step 1: Preprocess the incoming user question with the exact same pipeline
        cleaned_user_query = preprocess_text(user_question)

        # If user query contained only unknown symbols or punctuation
        if not cleaned_user_query.strip():
            return {
                "answer": FALLBACK_RESPONSE,
                "matched_question": None,
                "confidence": 0.0
            }

        # Step 2: Transform user query into a TF-IDF vector using our fitted vectorizer
        user_vector = self.vectorizer.transform([cleaned_user_query])

        # Step 3: Compute Cosine Similarity between user vector and all FAQ vectors
        # Result is an array of shape (1, num_faqs)
        similarity_scores = cosine_similarity(user_vector, self.faq_matrix)[0]

        # Step 4: Identify the best matching FAQ index and highest score
        best_index = int(similarity_scores.argmax())
        best_score = float(similarity_scores[best_index])
        rounded_confidence = round(best_score, 2)

        # Step 5: Check if the confidence meets our threshold
        if best_score < SIMILARITY_THRESHOLD:
            return {
                "answer": FALLBACK_RESPONSE,
                "matched_question": None,
                "confidence": rounded_confidence
            }

        # Step 6: Return the matched answer and metadata
        matched_faq = self.faqs[best_index]
        return {
            "answer": matched_faq["answer"],
            "matched_question": matched_faq["question"],
            "confidence": rounded_confidence
        }


# Global singleton instance for easy import in Flask
chatbot_instance = FAQChatbot()


def get_chatbot_response(question: str) -> dict:
    """
    Convenience function to get a response from the singleton chatbot instance.
    """
    return chatbot_instance.get_response(question)
