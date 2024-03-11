# protein-scatter

A map of proteins for exploration and discovery. Specifically to explore many local parts of proteins all at once. 

https://github.com/xnought/protein-scatter/assets/65095341/9cd9986c-c619-40a1-a4a5-784550670b64



This code uses [Foldseek](https://github.com/steineggerlab/foldseek)'s 3Di representation instead of amino acids to train a sequence model. The embeddings from the sequence model are then fed into UMAP for a global visualization.

What makes this system different? Here I explicitly model each protein as the interactions of it's internal 3D structure. I then compare across many different proteins for a global visualization.

## Models and Datasets

If you want to reproduce these results check the training code in the [`training/`](./training/) directory.

Note that UMAP transformation was does in python notebooks not in the python code.

The weights are saved in `checkpoint-large-3.pt` in this [ Google Drive ](https://drive.google.com/drive/folders/1FerixS81_qof0QD-k-0PN3kUSt8oBWLK?usp=sharing) as well as additional training data.

## Code References

See the paper (todo link) for more references that aren't just code references.

- Foldseek: [van Kempen M, Kim S, Tumescheit C, Mirdita M, Lee J, Gilchrist C, Söding J, and Steinegger M. Fast and accurate protein structure search with Foldseek. Nature Biotechnology, doi:10.1038/s41587-023-01773-0 (2023)](https://www.nature.com/articles/s41587-023-01773-0) to convert sequences into their 3Di representation for training.

- nanoGPT: [Andrej Karpathy](https://github.com/karpathy) for direct use and modification of causal self attention torch blocks.
	- https://github.com/karpathy/nanoGPT
 	- https://github.com/karpathy/ng-video-lecture

- USalign: [Chengxin Zhang, Morgan Shine, Anna Marie Pyle, Yang Zhang](https://github.com/pylelab/USalign) for use in the website backend to visualize pdb proteins superimposed on the query proteins.

