# 단어 → 숫자 매핑용 토크나이저

import pandas as pd

class MyTokenizer:
    """
    학습 데이터에 등장한 모든 단어를 기반으로 단어 사전을 만들고,
    문장을 숫자 리스트로 인코딩하거나, 숫자를 다시 문장으로 디코딩하는 클래스
    """

    def __init__(self, csv_path, min_freq=1):
        """
        csv_path: 학습에 사용할 CSV 파일 경로
        min_freq: 특정 단어가 등장한 최소 횟수 (희귀 단어는 제외)
        """
        self.word2idx = {"<PAD>": 0, "<START>": 1, "<END>": 2, "<UNK>": 3}
        self.idx2word = {0: "<PAD>", 1: "<START>", 2: "<END>", 3: "<UNK>"}
        self.vocab = set()

        self.build_vocab(csv_path, min_freq)

    def build_vocab(self, csv_path, min_freq):
        """
        모든 문장을 읽고 단어 사전을 구축함
        """
        df = pd.read_csv(csv_path)
        word_freq = {}

        for caption in df["caption"]:
            tokens = caption.strip().split()
            for token in tokens:
                word_freq[token] = word_freq.get(token, 0) + 1

        for word, freq in word_freq.items():
            if freq >= min_freq and word not in self.word2idx:
                idx = len(self.word2idx)
                self.word2idx[word] = idx
                self.idx2word[idx] = word
                self.vocab.add(word)

    def encode(self, sentence):
        """
        문장을 숫자 리스트로 변환
        """
        tokens = sentence.strip().split()
        ids = [self.word2idx.get(token, self.word2idx["<UNK>"]) for token in tokens]
        return [self.word2idx["<START>"]] + ids + [self.word2idx["<END>"]]

    def decode(self, token_ids):
        """
        숫자 리스트를 다시 문장으로 변환
        """
        words = [self.idx2word.get(idx, "<UNK>") for idx in token_ids]
        return " ".join(words)

    def vocab_size(self):
        """
        전체 단어 개수 반환
        """
        return len(self.word2idx)
