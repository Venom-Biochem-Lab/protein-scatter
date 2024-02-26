# protein-map

A map of proteins for exploration and discovery.

This code uses Foldseek's 3Di representation instead of amino acids to train a sequence model. The embeddings from the sequence model are then fed into UMAP.

## TODO

- [x] read from pdb file 3D center location of each amino acid (as $\alpha$ carbon for now)
- [x] extract features relevant to the 3D info
- [ ] Train sequence model on the new alphabet
- [ ] extract embeddings and visualize in 2D
- [ ] Train sequence model on the entire PDB
- [ ] extract embeddings and visualize in 2D
- [ ] create interface around it
