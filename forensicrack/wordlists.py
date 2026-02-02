import os


class WordlistManager:
    def __init__(self, wordlist_dir: str):
        self.wordlist_dir = wordlist_dir
        self.brockyou = os.path.join(wordlist_dir, "brockyou.txt")
        self.passphrases = os.path.join(wordlist_dir, "passphrases.txt")

    def escalating_lists(self):
        lists = []
        if os.path.exists(self.brockyou):
            lists.append(self.brockyou)
        if os.path.exists(self.passphrases):
            lists.append(self.passphrases)
        return lists