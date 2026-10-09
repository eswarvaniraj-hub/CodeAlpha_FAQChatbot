# 🤖 NovaMart AI FAQ Chatbot (CodeAlpha Internship - Task 2)

A lightweight, beginner-friendly, and 100% offline AI FAQ Chatbot web application built with **Python, Flask, NLTK, and Scikit-Learn**. 

The chatbot intelligently matches user inquiries against an FAQ knowledge base using **TF-IDF Vectorization** and **Cosine Similarity**, providing instant answers with confidence scoring and fallback handling.

---

## 🌟 Key Features

- **Accurate NLP Matching**: Preprocesses queries and computes cosine similarity with TF-IDF vectors.
- **Threshold Fallback**: Gracefully falls back to a friendly message if the confidence score is below `0.3`.
- **Modern Chat Interface**: Responsive UI with user & bot message bubbles, timestamps, typing indicator, auto-scroll, and match confidence badges.
- **Clickable Suggested Chips**: Quick-start question chips for instant interaction.
- **100% Offline & Free**: No paid APIs (like OpenAI), runs completely locally on your machine.
- **Modular Architecture**: Clean separation between backend web routes (`app.py`), NLP logic (`chatbot.py`), and FAQ data (`faqs.json`).

---

## 📁 Project Structure

```
faq-chatbot/
├── app.py              # Flask app routes (GET /, POST /ask)
├── chatbot.py          # NLP pipeline: Preprocessing, TF-IDF, Cosine Similarity
├── faqs.json           # Knowledge base with 20 realistic store FAQs
├── test_chatbot.py     # Automated test script with 5 evaluation test cases
├── requirements.txt    # Pinned Python package dependencies
├── README.md           # Setup instructions and documentation
├── templates/
│   └── index.html      # Modern chat interface structure
└── static/
    ├── style.css       # Clean styling, responsive layout, animations
    └── script.js       # Asynchronous fetch(), UI rendering, typing effect
```

---

## 🚀 Setup & Installation Guide

Follow these steps to set up and run the chatbot on your local machine:

### 1. Prerequisites
Ensure you have **Python 3.8+** installed. You can check by running:
```bash
python --version
```

### 2. Open Terminal in the Project Directory
Navigate to the project folder:
```bash
cd "c:\Users\Eswar\Desktop\FAQAI Codealpha"
```

### 3. Create and Activate a Virtual Environment (Recommended)

- **On Windows (PowerShell / Command Prompt):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```

- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
Install all required libraries using `requirements.txt`:
```bash
pip install -r requirements.txt
```

> **Note:** On first execution, the chatbot automatically checks and downloads necessary NLTK corpora (`punkt`, `stopwords`, `wordnet`) without manual setup.

---

## 🧪 Testing the NLP Engine

Before launching the web server, you can run the built-in test suite to verify the matching engine across 5 sample questions:

```bash
python test_chatbot.py
```

Expected output will display the user query, matched FAQ question, cosine confidence percentage, and fallback test verification.

---

## 🌐 Running the Web Application

Start the Flask development server:
```bash
python app.py
```

Once started, open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧠 How It Works (NLP Explanation for Internship Video)

The chatbot matches questions through a simple and powerful 5-step pipeline:

```
[User Question]
       │
       ▼
1. Preprocessing (Lowercase, Remove Punctuation, Tokenize, Remove Stopwords, Lemmatize)
       │
       ▼
2. TF-IDF Vectorization (Convert cleaned text into a numerical keyword vector)
       │
       ▼
3. Cosine Similarity (Calculate mathematical angle between User Vector and FAQ Vectors)
       │
       ▼
4. Threshold Evaluation (Is Best Score >= 0.3?)
      ├── YES ──> Return Matched FAQ Answer + Confidence Score
      └── NO  ──> Return Friendly Fallback Message
```

### 1. Text Preprocessing (NLTK)
- **Lowercasing**: Converts "Shipping" to "shipping" for consistency.
- **Punctuation Removal**: Strips `?`, `!`, `,` so punctuation does not distort words.
- **Tokenization**: Splits sentences into individual words.
- **Stopword Removal**: Filters out frequent filler words like `"is"`, `"the"`, `"at"`.
- **Lemmatization**: Reduces words to their root lemma (e.g., `"tracking"` &rarr; `"track"`, `"items"` &rarr; `"item"`).

### 2. TF-IDF (Term Frequency - Inverse Document Frequency)
- **Term Frequency (TF)**: How often a word appears in a specific FAQ question.
- **Inverse Document Frequency (IDF)**: Measures how rare or unique a word is across all FAQ questions. Rare keywords like `"refund"` or `"warranty"` get higher weights than common words.
- Produces a numerical vector representation for each question.

### 3. Cosine Similarity (Scikit-Learn)
- Measures the cosine of the angle between the user's vector and each FAQ vector in multi-dimensional space.
- Scores range from `0.0` (no overlap) to `1.0` (exact semantic match).
- The FAQ with the highest cosine score is selected.

### 4. Confidence Thresholding
- If the highest score is below `0.3`, the question is considered unanswerable or out-of-scope, and the bot displays a helpful fallback response asking the user to rephrase.

---

## ✏️ How to Add or Edit FAQs

You can easily expand the chatbot's knowledge base by editing [`faqs.json`](file:///c:/Users/Eswar/Desktop/FAQAI%20Codealpha/faqs.json):

1. Open `faqs.json` in any text editor.
2. Add a new JSON object to the list:
   ```json
   {
     "question": "Do you offer student discounts?",
     "answer": "Yes! Students can get an extra 10% off by verifying their student ID through StudentBeans at checkout."
   }
   ```
3. Save the file and restart the Flask app (`python app.py`). The model will automatically re-index the new questions!

---

## 🔮 Future Enhancements

1. **Semantic Embeddings (BERT / Sentence Transformers)**: Upgrade from bag-of-words TF-IDF to transformer embeddings (like `all-MiniLM-L6-v2`) to capture deep context and synonyms even with completely different vocabulary.
2. **Conversation History & Context**: Add session-based memory so the chatbot remembers previous user messages and handles follow-up questions.
3. **Admin Dashboard & Analytics**: Build a management page to view unanswered queries, track user satisfaction, and add new FAQs directly from the browser.
