import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class RerankModel():
    """
    Config rerank model AITeamVN/Vietnamese_Reranker
    """

    MAX_LENGTH = 2304
    tokenizer = AutoTokenizer.from_pretrained('AITeamVN/Vietnamese_Reranker')
    model = AutoModelForSequenceClassification.from_pretrained('AITeamVN/Vietnamese_Reranker')

    def __init__(self):
        """
        Set up GPU for reranker
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        
        # Warm-up
        with torch.no_grad():
            dummy_input = self.tokenizer([["test", "test"]], padding=True, truncation=True, return_tensors='pt', max_length=self.MAX_LENGTH)
            dummy_input = {k: v.to(self.device) for k, v in dummy_input.items()}
            self.model(**dummy_input)

    def rank(self, query: str, documents: list[str], top_k: int) -> list[str]:
        """
        Get top 5 documents
        """
        pairs = [[query, doc] for doc in documents]
        top_k = min(top_k, len(documents))

        with torch.no_grad():
            inputs = self.tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=self.MAX_LENGTH)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}  # Move inputs to GPU
            scores = self.model(**inputs, return_dict=True).logits.view(-1, ).float()

            topk = torch.topk(scores, k=top_k)
            top_indices = topk.indices.tolist()

            ranked_docs = [documents[i] for i in top_indices]
            return ranked_docs