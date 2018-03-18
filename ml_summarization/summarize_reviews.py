from __future__ import print_function
import argparse
from Summarizer import Summarizer

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--text", required=True,
                    help="text")
    ap.add_argument("-s", "--reaction_type", required=False)
    args = vars(ap.parse_args())

    txt = args["text"]
    re_type = args["reaction_type"]
    # print(re_type)
    summarizer = Summarizer()
    # with open('data.txt', 'r') as myfile:
    #     data = myfile.read()
    result = summarizer.get_a_random_summary_sentence(text=txt, reaction_type=re_type)
    print(result, end='')
