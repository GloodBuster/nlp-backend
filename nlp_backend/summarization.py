import nltk
import heapq
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


def summarize_text_with_heapq(text, language='spanish', summary_length=30):

    sentence_list = nltk.sent_tokenize(text)
    stopwords = nltk.corpus.stopwords.words(language)

    word_frequencies = {}
    for word in nltk.word_tokenize(text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    maximum_frequency = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequency)

    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < summary_length:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    summary_sentences = heapq.nlargest(
        7, sentence_scores, key=sentence_scores.get)

    summary = ' '.join(summary_sentences)

    return summary


def summarize_text_with_sumy(text, language='spanish', summary_length=30):

    parser = PlaintextParser.from_string(text, Tokenizer(language))
    stemmer = Stemmer(language)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)

    summary_sentences = []
    for sentence in summarizer(parser.document, summary_length):
        summary_sentences.append(sentence._text)

    summary = ' '.join(summary_sentences)

    return summary
