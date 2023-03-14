import openai, numpy as np, time
from dotenv import dotenv_values
from redis_client import RedisClient
config = dotenv_values(".env")

openai.api_key = config["OPENAI_API_KEY"]
openai.organization = config["OPENAI_ORG_ID"]

# retrieve the embedding from the redis cache
# if it doesn't exist, create it and store it in the cache
# then return it
def get_embedding(text):
    redis_client = RedisClient(host=config["REDIS_HOST"], port=config["REDIS_PORT"])
    key = text
    if not redis_client.exists(key):
        time.sleep(1)
        print("creating embedding for: " + text)
        response = openai.Embedding.create(
            input=text,
            model = "text-embedding-ada-002"
        )
        embeddings = response['data'][0]['embedding']
        redis_client.set(key, embeddings)
    else:
        embeddings = redis_client.get(key)
    return embeddings

# calculate the cosine similarity between two embeddings
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# calculate the similarity between two texts
def similarity(text1, text2):
    embedding1 = get_embedding(text1)
    embedding2 = get_embedding(text2)
    return cosine_similarity(embedding1, embedding2)

# calculate the similarity between a text and a list of texts
def similarity_list(text, text_list):
    embedding1 = get_embedding(text)
    similarities = []
    for text2 in text_list:
        embedding2 = get_embedding(text2)
        similarities.append(cosine_similarity(embedding1, embedding2))
    return similarities

# calculate the similarity between a text and a list of texts
# and return the most similar text
def most_similar(text, text_list):
    similarities = similarity_list(text, text_list)
    return text_list[similarities.index(max(similarities))]

# calculate the similarity between a text and a list of texts
# and return the most similar text and its similarity
def most_similar_with_similarity(text, text_list):
    similarities = similarity_list(text, text_list)
    return text_list[similarities.index(max(similarities))], max(similarities)

# calculate the similarity between a text and a list of texts
# and return the most similar text and its similarity
# if the similarity is below a threshold, return None
def most_similar_with_similarity_threshold(text, text_list, threshold):
    similarities = similarity_list(text, text_list)
    max_similarity = max(similarities)
    if max_similarity < threshold:
        return None, max_similarity
    return text_list[similarities.index(max_similarity)], max_similarity


text_list = ['Los felinos dicen', 'Los caninos dicen',\
             'Los bovinos dicen', 'Tengo un terreno en ayacucho', 'Tengo una casa en Piura']

text = 'meaw'

print(f'El texto {text} es similar a: {most_similar(text, text_list)}')


