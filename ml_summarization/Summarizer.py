from summarization_utils import *
import subprocess
import json
import numpy as np


class Summarizer(object):

    def get_a_random_summary_sentence(self, text, reaction_type=None):
        sentences = summarize_simple_text(text=text, no_of_sentences=NO_OF_EXTRACTED_SENTENCES)
        no_of_sentences = min(NO_OF_EXTRACTED_SENTENCES, len(sentences))
        positive_sentences = []
        negative_sentences = []
        if reaction_type is None:
            if no_of_sentences > 0:
                random_sample = np.random.randint(0, no_of_sentences)
                sentence = sentences[random_sample]
                sentiment_json = subprocess.check_output(
                    ['curl', '-d', 'text=' + sentence, 'http://text-processing.com/api/sentiment/'])
                json_data = json.loads(sentiment_json)
                negative = json_data[u'probability'][u'neg']
                positive = json_data[u'probability'][u'pos']

                result = 'Here is a{} review: {}'

                if negative > 0.75:
                    result = result.format('n ' + OVERWHELMINGLY_POSITIVE, sentence)
                elif negative > 0.55:
                    result = result.format(' ' + NEGATIVE, sentence)
                elif positive > 0.75:
                    result = result.format('n ' + OVERWHELMINGLY_POSITIVE, sentence)
                elif positive > 0.55:
                    result = result.format(' ' + POSITIVE, sentence)
                else:
                    result = result.format(' ' + NEUTRAL, sentence)
                return result
            else:
                return 'Couldn\'t find any relevant reviews'
        else:
            for s in sentences:
                sentiment_json = subprocess.check_output(
                    ['curl', '-d', 'text=' + s, 'http://text-processing.com/api/sentiment/'])
                json_data = json.loads(sentiment_json)
                if json_data[u'label'] == LABEL_POS:
                    positive_sentences.append(s)
                else:
                    negative_sentences.append(s)
            if reaction_type == TYPE_POSITIVE and len(positive_sentences) > 0:
                random_sample = np.random.randint(0, len(positive_sentences))
                sentence = positive_sentences[random_sample]
                result = 'Here is a positive review: {}'.format(sentence)
            elif reaction_type == TYPE_NEGATIVE and len(negative_sentences) > 0:
                random_sample = np.random.randint(0, len(negative_sentences))
                sentence = negative_sentences[random_sample]
                result = 'Here is a negative review: {}'.format(sentence)
            else:
                result = 'Couldn\'t find a {} review'.format('positive' if reaction_type == TYPE_POSITIVE else 'negative')
            return result
