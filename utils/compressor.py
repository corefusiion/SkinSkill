import sys

def compress(text):
    """
    Comprime o texto removendo palavras desnecessárias (estilo Caveman).
    Mantém apenas substantivos, verbos e termos técnicos.
    """
    # Lista simples de palavras para remover
    stop_words = ["o", "a", "os", "as", "um", "uma", "de", "do", "da", "em", "no", "na", "para", "com", "que", "é", "são"]
    
    words = text.split()
    compressed = [w for w in words if w.lower() not in stop_words]
    
    return " ".join(compressed)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(compress(" ".join(sys.argv[1:])))
