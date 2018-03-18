import nltk

from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import MatrixSimilarity
from gensim.summarization.bm25 import get_bm25_weights as _bm25_weights
from gensim.summarization.graph import Graph
from gensim.summarization.pagerank_weighted import pagerank_weighted
from gensim.summarization.textcleaner import clean_text_by_sentences
from sklearn.metrics.pairwise import cosine_similarity


WORD_COUNT = 1
TF = 2
TFIDF = 3

OVERWHELMINGLY_NEGATIVE = 'overwhelmingly negative'
NEGATIVE = 'negative'
NEUTRAL = 'neutral'
POSITIVE = 'positive'
OVERWHELMINGLY_POSITIVE = 'overwhelmingly positive'

MIN_SENTENCE_LENGTH = 5
MAX_SENTENCE_LENGTH = 50

LABEL_POS = 'pos'
LABEL_NEG = 'neg'

TYPE_POSITIVE = 'positive'
TYPE_NEGATIVE = 'negative'

NO_OF_EXTRACTED_SENTENCES = 10


def summarize_simple_text(text, no_of_sentences=10):
    text = text.replace('.', '. ')
    sentences = nltk.sent_tokenize(text)
    if len(sentences) > 0:
        ratio = float(no_of_sentences) / len(sentences)
    else:
        ratio = 0
    # print("RATIO: " + str(ratio))
    rez, scores = summarize_text_duplicates(text, ratio, summarization_method=TFIDF,
                                            all_documents_text=text)

    return rez


def _build_corpus(sentences):
    split_tokens = [sentence.token.split() for sentence in sentences]
    dictionary = Dictionary(split_tokens)
    return [dictionary.doc2bow(token) for token in split_tokens]


def _build_hashable_corpus(corpus):
    return [tuple(doc) for doc in corpus]


def build_graph(sequence):
    graph = Graph()
    for item in sequence:
        if not graph.has_node(item):
            graph.add_node(item)
    return graph


def _word_count_weights(documents):
    doc_sets = map(lambda doc: set(doc), documents)

    weights = []
    for i, doc1 in enumerate(doc_sets):
        weights.append([])
        for j, doc2 in enumerate(doc_sets):
            weights[i].append(float(len(doc1 & doc2)) / min(len(doc1), len(doc2)))
    return weights


def _tf_weights(corpus):
    index = MatrixSimilarity(corpus)
    weights = index[corpus]

    return weights


def _tfidf_weights(corpus):
    tfidf = TfidfModel(corpus, normalize=False)
    tfidf_corpus = tfidf[corpus]
    index = MatrixSimilarity(tfidf_corpus)
    weights = index[tfidf_corpus]

    return weights


def _tfidf_weights2(corpus, corpus_all):
    tfidf = TfidfModel(corpus_all, normalize=False)
    tfidf_corpus = tfidf[corpus]
    index = MatrixSimilarity(tfidf_corpus)
    weights = index[tfidf_corpus]

    return weights


def _doc2vec_weights(model, documents, sentences, corpus, alpha=0.01, steps=1000):
    all_docs = [list(doc) for doc in documents]
    doc_sets = _get_important_sentences(sentences, corpus, all_docs)
    doc_sets = _format_results(doc_sets, True)

    vec = []
    for doc in doc_sets:
        words_sentence = nltk.word_tokenize(doc)
        words_sentence = [word.lower() for word in words_sentence]
        vec.append(model.infer_vector(words_sentence, alpha=alpha, steps=steps))

    weights = cosine_similarity(vec)

    return weights


def _set_graph_edge_weights(graph, weight_function=_bm25_weights, graph_nodes_dict=None, weight_threshold=0.0001):
    documents = graph.nodes()

    if graph_nodes_dict is None:
        weights = weight_function(documents)
    else:
        weights = weight_function

    for i, doc1 in enumerate(documents):
        for j, doc2 in enumerate(documents):

            if graph_nodes_dict is not None:
                i_weights = graph_nodes_dict[doc1]
                j_weights = graph_nodes_dict[doc2]
                weights_ij = weights[i_weights][j_weights]
                weights_ji = weights[j_weights][i_weights]
            else:
                weights_ij = weights[i][j]
                weights_ji = weights[j][i]

            if i == j or weights_ij < weight_threshold:
                continue

            sentence_1 = documents[i]
            sentence_2 = documents[j]

            edge_1 = (sentence_1, sentence_2)
            # ADDED IF
            if not graph.has_edge(edge=edge_1):
                graph.add_edge(edge_1, weights_ij)

    # Handles the case in which all similarities are zero.
    # The resultant summary will consist of random sentences.
    if all(graph.edge_weight(edge) == 0 for edge in graph.edges()):
        _create_valid_graph(graph)


def _create_valid_graph(graph):
    nodes = graph.nodes()

    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if i == j:
                continue

            edge = (nodes[i], nodes[j])

            if graph.has_edge(edge):
                graph.del_edge(edge)

            graph.add_edge(edge, 1)


def _get_important_sentences(sentences, corpus, important_docs):
    hashable_corpus = _build_hashable_corpus(corpus)
    sentences_by_corpus = dict(zip(hashable_corpus, sentences))
    return [sentences_by_corpus[tuple(important_doc)] for important_doc in important_docs]


def _format_results(extracted_sentences, split):
    if split:
        return [sentence.text for sentence in extracted_sentences]
    # return "\n".join([sentence.text for sentence in extracted_sentences])
    return [sentence.text for sentence in extracted_sentences]


def get_sentence_word_count(sentence):
    return len(nltk.word_tokenize(sentence))


def summarize_text_duplicates(text, ratio, summarization_method=WORD_COUNT, all_documents_text=None):
    sentences = clean_text_by_sentences(text)
    sentences = [s for s in sentences if MIN_SENTENCE_LENGTH <= get_sentence_word_count(s.text) <= MAX_SENTENCE_LENGTH]
    corpus = _build_corpus(sentences)

    hashable_corpus = _build_hashable_corpus(corpus)
    graph = build_graph(hashable_corpus)

    if summarization_method == WORD_COUNT:
        weights = _word_count_weights(graph.nodes())
    elif summarization_method == TF:
        # Except ValueError: cannot index a corpus with zero features
        # (you must specify either `num_features` or
        # a non-empty corpus in the constructor)
        if len(graph.nodes()) == 0:
            return '', [0]
        else:
            weights = _tf_weights(graph.nodes())
    elif summarization_method == TFIDF:
        all_sentences = clean_text_by_sentences(all_documents_text)
        corpus_all = _build_corpus(all_sentences)
        hashable_corpus_all = _build_hashable_corpus(corpus_all)
        graph_all = build_graph(hashable_corpus_all)

        # Except ValueError: cannot index a corpus with zero features
        # (you must specify either `num_features` or
        # a non-empty corpus in the constructor)
        if len(graph.nodes()) <= 1:
            # makes get_all_text = True
            ratio = len(graph.nodes())
            weights = [[0 for _ in range(len(graph.nodes()))]
                       for _ in range(len(graph.nodes()))]
        else:
            weights = _tfidf_weights2(graph.nodes(), graph_all.nodes())

    pagerank_weights = [0 for docs in range(len(graph.nodes()))]
    graph_nodes_dict = dict(zip(graph.nodes(), list(range(0, len(graph.nodes())))))
    final_sentences = []
    sentences_score = []
    pagerank_scores = {}

    _set_graph_edge_weights(graph, weights, graph_nodes_dict)

    get_all_text = False
    if (int(len(corpus) * ratio) > len(graph.nodes()) - 2 or (
            len(graph.nodes()) <= 2 and int(len(corpus) * ratio) > 0)):
        get_all_text = True
    steps = min(int(len(corpus) * ratio), len(graph.nodes()) - 2)

    # print('Graph nodes: ' + str(len(graph.nodes())))

    for _ in range(steps):
        pagerank_scores = pagerank_weighted(graph)
        for pagerank_key in pagerank_scores.keys():
            doc = graph_nodes_dict[pagerank_key]
            pagerank_scores[pagerank_key] -= pagerank_weights[doc]

        hashable_corpus.sort(key=lambda doc: pagerank_scores.get(doc, 0), reverse=True)
        sentences_score.append(pagerank_scores[hashable_corpus[0]])
        most_important_docs = [list(hashable_corpus[0])]

        extracted_sentences = _get_important_sentences(sentences, corpus, most_important_docs)
        final_sentences.append(extracted_sentences[0])

        for pagerank_key in pagerank_scores.keys():
            doc1 = graph_nodes_dict[pagerank_key]
            doc2 = graph_nodes_dict[tuple(most_important_docs[0])]
            pagerank_weights[doc1] += weights[doc1][doc2]

        graph.del_node(tuple(most_important_docs[0]))
        hashable_corpus = filter(lambda doc: doc != tuple(most_important_docs[0]), hashable_corpus)

    if get_all_text:
        for node in graph.nodes():
            extracted_sentences = _get_important_sentences(sentences, corpus, [list(node)])
            final_sentences.append(extracted_sentences[0])

            if not pagerank_scores:
                if len(sentences_score) == 0:
                    sentences_score.append(0)
                else:
                    sentences_score.append(sentences_score[-1])
            else:
                sentences_score.append(pagerank_scores[node])

            # When you want to extract only one sentence and there are only two nodes in graph.
            if int(len(corpus) * ratio) == 1:
                break

    final_sentences = _format_results(final_sentences, False)
    return final_sentences, sentences_score
