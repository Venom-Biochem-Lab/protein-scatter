# protein-map

Like a map of the land of proteins used to model close similarity and explore neighbors

## TODO

- [x] read from pdb file 3D center location of each amino acid (as $\alpha$ carbon for now)
- [ ] extract features relevant to the 3D info
	- [ ] see if relative position of top $k$ is useful
	- [ ] train a vector quantized AE to learn an alphabet rp3Di on 32 vectors (like what foldseek does, but simpler)
		- [ ] don't include aa info
		- [ ] include aa info
- [ ] Train sequence model on the new alphabet
- [ ] extract embeddings and visualize in 2D
- [ ] Train sequence model on the entire PDB
- [ ] extract embeddings and visualize in 2D
- [ ] create interface around it