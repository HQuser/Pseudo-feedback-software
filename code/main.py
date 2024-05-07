from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from helper import get_all_verticals, extract_text, generate_summary

model_name_generation = "valhalla/t5-base-e2e-qg"
tokenizer_generation = AutoTokenizer.from_pretrained(model_name_generation)
model_generation = AutoModelForSeq2SeqLM.from_pretrained(model_name_generation)

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load the Paraphrase-MiniLM-L6-v2 model and tokenizer
model_name_semantic = "sentence-transformers/paraphrase-MiniLM-L6-v2"
tokenizer_semantic = AutoTokenizer.from_pretrained(model_name_semantic)
model_semantic = AutoModelForSequenceClassification.from_pretrained(model_name_semantic)
model_semantic.eval()

import nltk
nltk.download('punkt')

def generate_questions(results):
    pool = list()
    for text in results:
        # Tokenize input text
        inputs = tokenizer_generation(text, return_tensors="pt")

        # Generate questions
        outputs = model_generation.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=64,  # Maximum length of generated questions
            num_beams=4,  # Number of beams for beam search
            early_stopping=True,
            no_repeat_ngram_size=2,  # Avoid repetition of n-grams
            num_return_sequences=1,  # Number of questions to generate
        )

        # Decode the generated questions
        questions = [tokenizer_generation.decode(output, skip_special_tokens=True) for output in outputs]
        pool.append(questions)
    # flatten questions
    from itertools import chain
    pool = list(chain.from_iterable(pool))
    # filter irrelevant queries that do not adhere to 5W communication
    prefixes = ["what", "why", "who", "how", "where"]
    # Filter strings (convert both string and prefixes to lowercase for case-insensitive comparison)
    pool = [s for s in pool if any(s.lower().startswith(prefix.lower()) for prefix in prefixes)]

    return pool


def rank_queries(queries, q):
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
    embeddings = model.encode(queries)
    q = model.encode("an example sentence")

    query_similarity_list = list()
    for c, e in enumerate(embeddings):
        question_embedding = e.reshape(1, -1)
        q_embedding = q.reshape(1, -1)
        # Calculate cosine similarity
        similarity = cosine_similarity(question_embedding, q_embedding)[0][0]

        #if(similarity > 0.5):
        query_similarity_list.append((queries[c], similarity))

    if not query_similarity_list:
        return list()

    return sorted(query_similarity_list, reverse=True, key=lambda x: x[1])


search_results = get_all_verticals()
text_data = extract_text(search_results)
summarized_res = generate_summary(text_data)
questions_pool = generate_questions(summarized_res)
ranked_queries = rank_queries(questions_pool, "mcdonald location")
print(ranked_queries)