# protein-map

A map of proteins for exploration and discovery.

This code uses [Foldseek](https://github.com/steineggerlab/foldseek)'s 3Di representation instead of amino acids to train a sequence model. The embeddings from the sequence model are then fed into UMAP for a global visualization.

What makes this system different? Here I explicitly model each protein as the interactions of it's internal 3D structure. I then compare across many different proteins for a global visualization.

## TODO

- [x] read from pdb file 3D center location of each amino acid (as $\alpha$ carbon for now)
- [x] extract features relevant to the 3D info
- [ ] Train sequence model on the new alphabet
	- [x] Create a small dataset (3 train, 1 val of relatively small proteins)
	- [x] Create a transformer that can overfit that dataset (simply)
- [x] extract embeddings and visualize in 2D
- [x] filter all of PDB dataset down to ~100k proteins of length between 64 and 2048
- [ ] Train sequence model on subset of PDB for a ton of iterations (might take many days)
- [ ] extract embeddings and visualize in 2D
- [ ] create interface around it


## References

- Foldseek: [van Kempen M, Kim S, Tumescheit C, Mirdita M, Lee J, Gilchrist C, Söding J, and Steinegger M. Fast and accurate protein structure search with Foldseek. Nature Biotechnology, doi:10.1038/s41587-023-01773-0 (2023)](https://www.nature.com/articles/s41587-023-01773-0)

- [Andrej Karpathy](https://github.com/karpathy)
	- https://github.com/karpathy/nanoGPT
 	- https://github.com/karpathy/ng-video-lecture