import torch
import torch.nn as nn
from torch.nn import functional as F

device = "cuda" if torch.cuda.is_available() else "cpu"
torch.manual_seed(1337)


class CausalSelfAttention(nn.Module):
    def __init__(self, n_embd, n_head, bias, dropout):
        super().__init__()
        assert n_embd % n_head == 0
        # key, query, value projections for all heads, but in a batch
        self.c_attn = nn.Linear(n_embd, 3 * n_embd, bias=bias)
        # output projection
        self.c_proj = nn.Linear(n_embd, n_embd, bias=bias)
        # regularization
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)
        self.n_head = n_head
        self.n_embd = n_embd
        self.dropout = dropout

    def forward(self, x):
        (
            B,
            T,
            C,
        ) = x.size()  # batch size, sequence length, embedding dimensionality (n_embd)

        # calculate query, key, values for all heads in batch and move head forward to be the batch dim
        q, k, v = self.c_attn(x).split(self.n_embd, dim=2)
        k = k.view(B, T, self.n_head, C // self.n_head).transpose(
            1, 2
        )  # (B, nh, T, hs)
        q = q.view(B, T, self.n_head, C // self.n_head).transpose(
            1, 2
        )  # (B, nh, T, hs)
        v = v.view(B, T, self.n_head, C // self.n_head).transpose(
            1, 2
        )  # (B, nh, T, hs)

        # causal self-attention; Self-attend: (B, nh, T, hs) x (B, nh, hs, T) -> (B, nh, T, T)
        y = torch.nn.functional.scaled_dot_product_attention(
            q,
            k,
            v,
            attn_mask=None,
            dropout_p=self.dropout if self.training else 0,
            is_causal=True,
        )
        y = (
            y.transpose(1, 2).contiguous().view(B, T, C)
        )  # re-assemble all head outputs side by side

        # output projection
        y = self.resid_dropout(self.c_proj(y))
        return y


class Block(nn.Module):
    def __init__(self, n_embd, n_head, bias, dropout):
        super().__init__()
        self.ln_1 = nn.LayerNorm(n_embd, bias=bias)
        self.attn = CausalSelfAttention(n_embd, n_head, bias, dropout)
        self.ln_2 = nn.LayerNorm(n_embd, bias=bias)
        self.mlp = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd, bias=bias),
            nn.ReLU(),
            nn.Linear(4 * n_embd, n_embd, bias=bias),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x


class GPT(nn.Module):
    def __init__(
        self,
        vocab_size,
        n_embd,
        n_head,
        bias=True,
        n_layer=4,
        dropout=0.0,
        block_size=64,
    ):
        super().__init__()
        self.block_size = block_size
        self.token_embedding_table = nn.Embedding(
            vocab_size, n_embd
        )  # (vocab_size, n_embd) (n_embd is just Channels C)
        self.position_embedding_table = nn.Embedding(
            block_size, n_embd
        )  # so each character knows where it is in the sequence
        self.blocks = nn.Sequential(
            *[Block(n_embd, n_head, bias, dropout) for _ in range(n_layer)]
        )
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)

    def forward(self, idx, targets=None):
        """idx is the context and is shape (B, T)"""
        B, T = idx.shape

        # here we select out embeddings for all the tokens up to T and encode positions
        tok_embd = self.token_embedding_table(idx)  # (B, T, C)
        pos_embd = self.position_embedding_table(
            torch.arange(T, device=device)
        )  # select vectors based on context positions
        x = tok_embd + pos_embd

        # ATN
        embedding = self.blocks(x)
        x = self.ln_f(embedding)

        # MLP at end
        logits = self.lm_head(x)

        if targets is None:
            loss = None
        else:
            # generally speaking, this only happens during training
            B, T, C = logits.shape
            logits = logits.view(B * T, C)
            targets = targets.view(
                B * T
            )  # each index is the target of each row in logits
            loss = F.cross_entropy(logits, targets)

        # logits is shape (B, T, C) at inference time and (B*T, C) at train
        return logits, loss, embedding

    def seq_embeddings(self, seq):
        all_embeds = []
        B, T = seq.shape
        for i in range(0, seq.shape[1], self.block_size):
            d = seq[:, i : i + self.block_size]
            _, _, embeddings = self(d)
            embed = embeddings[
                :, -1, :
            ]  # pluck out the last embeddings (full block_size)
            all_embeds.append(embed)
        return torch.stack(all_embeds).squeeze()

    def generate(self, idx, max_new_tokens):
        # idx is (B, T) array of indices in the current context
        for _ in range(max_new_tokens):
            # crop idx to the last block_size tokens
            idx_cond = idx[:, -self.block_size :]
            # get the predictions
            logits, loss, _ = self(idx_cond)
            # focus only on the last time step
            logits = logits[:, -1, :]  # becomes (B, C)
            # apply softmax to get probabilities
            probs = F.softmax(logits, dim=-1)  # (B, C)
            # sample from the distribution
            idx_next = torch.multinomial(probs, num_samples=1)  # (B, 1)
            # append sampled index to the running sequence
            idx = torch.cat((idx, idx_next), dim=1)  # (B, T+1)
        return idx
