# protein-scatter

A map of proteins for exploration and discovery. Specifically to explore many local parts of proteins all at once. 

This code uses [Foldseek](https://github.com/steineggerlab/foldseek)'s 3Di representation instead of amino acids to train a sequence model. The embeddings from the sequence model are then fed into UMAP for a global visualization.

What makes this system different? Here I explicitly model each protein as the interactions of it's internal 3D structure. I then compare across many different proteins for a global visualization.

## References

- Foldseek: [van Kempen M, Kim S, Tumescheit C, Mirdita M, Lee J, Gilchrist C, Söding J, and Steinegger M. Fast and accurate protein structure search with Foldseek. Nature Biotechnology, doi:10.1038/s41587-023-01773-0 (2023)](https://www.nature.com/articles/s41587-023-01773-0) to convert sequences into their 3Di representation for training.

- nanoGPT: [Andrej Karpathy](https://github.com/karpathy) for direct use and modification of causal self attention torch blocks.
	- https://github.com/karpathy/nanoGPT
 	- https://github.com/karpathy/ng-video-lecture

- USalign: [Chengxin Zhang, Morgan Shine, Anna Marie Pyle, Yang Zhang](https://github.com/pylelab/USalign) for use in the website backend to visualize pdb proteins superimposed on the query proteins.

