import random, json, pickle, numpy as np  #, nltk

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer

from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Input
from keras.optimizers import SGD

#nltk.download('punkt')
#nltk.download('wordnet')

def simpleTokenizer(text):
    return text.split()

class Trainer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.ignore_words = set("!@#$%^&*?")
        self.path = "E:/guac_data/nlp_files"
        self.words = []
        self.classes = []
        self.documents = []
        self.vectorizer = TfidfVectorizer(tokenizer=simpleTokenizer, token_pattern=None)
        self.loadIntents()
        self.processData()

    def loadIntents(self):
        try:
            with open(f"{self.path}/intents.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.intents = data['intents']
        except Exception as e:
            raise Exception(f"Failed to load intents file: {e}")

    def tokenizeAndLemmatize(self, text):
        tokens = word_tokenize(text.lower())
        return [
            self.lemmatizer.lemmatize(token)
            for token in tokens if token not in self.ignore_words
        ]

    def processData(self):
        for intent in self.intents:
            tag = intent['tag']
            self.classes.append(tag)
            for pattern in intent['patterns']:
                tokens = self.tokenizeAndLemmatize(pattern)
                self.words.extend(tokens)
                self.documents.append((' '.join(tokens), tag))

        self.words = sorted(list(set(self.words)))
        self.classes = sorted(list(set(self.classes)))

    def prepareTrainingData(self):
        # Fit the vectorizer once
        all_sentences = [doc[0] for doc in self.documents]
        self.vectorizer.fit(all_sentences)

        training = []
        for sentence, tag in self.documents:
            x_vector = self.vectorizer.transform([sentence]).toarray()[0]
            y_vector = [0] * len(self.classes)
            y_vector[self.classes.index(tag)] = 1
            training.append((x_vector, y_vector))

        random.shuffle(training)
        training = np.array(training, dtype=object)
        train_x = list(training[:, 0])
        train_y = list(training[:, 1])

        return train_x, train_y

    def buildAndTrainModel(self):
        train_x, train_y = self.prepareTrainingData()

        model = Sequential()
        model.add(Input(shape=(len(train_x[0]),)))
        model.add(Dense(128, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(len(train_y[0]), activation='softmax'))

        # Updated: use 'learning_rate' instead of deprecated 'lr'
        sgd = SGD(learning_rate=1e-2, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

        model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=10, verbose=1)

        # Save the model
        model.save(f'{self.path}/chatbot_model.keras')

        # Save training data, vectorizer, and metadata
        with open(f"{self.path}/training_data", "wb") as f:
            pickle.dump({
                'words': self.words,
                'classes': self.classes,
                'train_x': train_x,
                'train_y': train_y
            }, f)

        with open(f"{self.path}/vectorizer.pkl", "wb") as f:
            pickle.dump(self.vectorizer, f)


class Testing:
    def __init__(self):
        self.path = "E:/guac_data/nlp_files"
        self.lemmatizer = WordNetLemmatizer()
        self.context = {}
        self.ERROR_THRESHOLD = 0.5
        self.ignore_words = set("!@#$%^&*?")

        try:
            with open(f"{self.path}/intents.json", 'r', encoding='utf-8') as f:
                self.intents = json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load intents file: {e}")

        try:
            with open(f"{self.path}/training_data", 'rb') as f:
                data = pickle.load(f)
                self.words = data['words']
                self.classes = data['classes']
        except Exception as e:
            raise Exception(f"Failed to load training data: {e}")

        try:
            self.model = load_model(f"{self.path}/chatbot_model.keras")
        except Exception as e:
            raise Exception(f"Failed to load model: {e}")

        # Initialize and fit TF-IDF vectorizer once
        with open(f"{self.path}/vectorizer.pkl", "rb") as f:
            self.vectorizer = pickle.load(f)


    def preprocess(self, sentence):
        tokens = word_tokenize(sentence.lower())
        lemmas = [
            self.lemmatizer.lemmatize(token)
            for token in tokens if token not in self.ignore_words
        ]
        return ' '.join(lemmas)

    def vectorize(self, sentence):
        processed = self.preprocess(sentence)
        vector = self.vectorizer.transform([processed]).toarray()

        return vector

    def classify(self, sentence):
        input_vector = self.vectorize(sentence)
        predictions = self.model.predict(input_vector, verbose=0)[0]
        results = [
            (self.classes[i], float(prob))
            for i, prob in enumerate(predictions) if prob > self.ERROR_THRESHOLD
        ]
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def getIntentResponse(self, tag, userID):
        for intent in self.intents.get('intents', []):
            if intent['tag'] == tag:
                # Check for filter/context
                if 'filter' in intent and self.context.get(userID) != intent['filter']:
                    continue

                if 'set' in intent:
                    self.context[userID] = intent['set']

                return random.choice(intent['responses'])
        return None

    def results(self, sentence, userID):
        if sentence.isdecimal() and self.context.get(userID) == "historydetails":
            return self.classify('ordernumber')
        return self.classify(sentence)

    def response(self, sentence, userID='GuacBot'):

        classified_results = self.results(sentence, userID)

        lookup = False
        if self.isLookup(sentence):
            lookup = True

        if not classified_results:
            return "else"

        else:
            highest = ("else", 0)
            for tag, confidence in classified_results:
                if lookup and tag.startswith("lookup"):
                    confidence = confidence * 1.2
                if confidence > highest[1]:
                    highest = (tag, confidence)
            return self.getIntentResponse(highest[0], userID)



import requests, re
from ddgs import DDGS
from bs4 import BeautifulSoup

def isLookup(sentence):
        sentence = sentence.lower()

        # You can extract these into a config file if needed
        patterns = [
            r"\b(current|latest|today|now)\b.*\b(weather|news|price|score|trending|cases|stats)\b",
            r"\bwhat('?s| is)?\b.*\b(stock|score|price|weather|news|cases|trending)\b",
            r"\bhow many\b.*\b(cases|followers|deaths|votes)\b",
            r"\b(is|are)\b.*\b(open|playing|live|trending)\b.*\btoday\b",
            r"\bwhen\b.*\b(game|match|event|sale|deadline)\b",
            r"\bcheck\b.*\b(weather|news|score|stats|traffic)\b",
            r"\bfind\b.*\b(update|info|information|price|stats)\b",
            r"\blook( up| for)?\b.*\b(score|weather|price|news|event)\b",
        ]

        for pattern in patterns:
            if re.search(pattern, sentence):
                return True

        return False

def parseSearchResults(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    title = soup.title.string.strip() if soup.title else "No title found."

    # Extract clean paragraph text
    paragraphs = soup.find_all('p')
    paragraph_lists = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    paragraph_texts = " ".join(paragraph_lists)

    return title, paragraph_texts

def search(query, max_results):

    results = DDGS().text(query,
                          safesearch="off",
                          max_results=max_results,
                          backend="html")

    responses = ""
    
    if not results:
        responses = "No search results found."
    else:
        headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
                "From": "josef.ryan.caraballo@gmail.com"
            }

        
        
        for i, result in enumerate(results, 1):
            url = result["href"]

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                title, content = parseSearchResults(response.content)
                responses = f"{responses}Source {i}: ({title}) {content}\n"

    return responses # Returns a string with all the search results concatenated