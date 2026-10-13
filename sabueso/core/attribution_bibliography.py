"""Offline resource descriptions; never DOI-enriched.

These works describe resources, not the experimental findings in their entries.
Metadata sources are recorded in docs/content/user/attribution.md.
"""

from copy import deepcopy

_DESCRIPTIONS = {
    "gnomAD": {
        "id": "url:https://gnomad.broadinstitute.org/api",
        "type": "dataset",
        "title": "gnomAD GraphQL API",
        "url": "https://gnomad.broadinstitute.org/api",
    },
    "UniProtKB search": {
        "id": "url:https://rest.uniprot.org/uniprotkb/search",
        "type": "dataset",
        "title": "UniProtKB search API",
        "url": "https://rest.uniprot.org/uniprotkb/search",
    },
    "OMA": {
        "id": "url:https://omabrowser.org/api",
        "type": "dataset",
        "title": "OMA REST API",
        "url": "https://omabrowser.org/api",
    },
    "UniRef": {
        "id": "url:https://rest.uniprot.org/uniref",
        "type": "dataset",
        "title": "UniProt Reference Clusters (UniRef)",
        "url": "https://rest.uniprot.org/uniref",
    },
    "GTEx": {
        "id": "url:https://gtexportal.org/",
        "type": "dataset",
        "title": "Genotype-Tissue Expression (GTEx) Portal",
        "url": "https://gtexportal.org/",
    },
    "NCBI Taxonomy": {
        "id": "url:https://www.ncbi.nlm.nih.gov/taxonomy",
        "type": "dataset",
        "title": "NCBI Taxonomy",
        "url": "https://www.ncbi.nlm.nih.gov/taxonomy",
    },
    "BRENDA": {
        "id": "doi:10.1093/nar/gkaf1113",
        "type": "article-journal",
        "title": "BRENDA in 2026: a Global Core Biodata Resource for functional enzyme and metabolic data within the DSMZ Digital Diversity",
        "doi": "10.1093/nar/gkaf1113",
        "url": "https://doi.org/10.1093/nar/gkaf1113",
    },
    "Pharos/TCRD": {
        "id": "url:https://pharos.nih.gov/",
        "type": "dataset",
        "title": "Pharos / Target Central Resource Database target metadata",
        "url": "https://pharos.nih.gov/",
    },
    "DepMap": {
        "id": "doi:10.25452/figshare.plus.27993248.v1",
        "type": "dataset",
        "title": "DepMap 24Q4 Public",
        "doi": "10.25452/figshare.plus.27993248.v1",
        "url": "https://doi.org/10.25452/figshare.plus.27993248.v1",
    },
    "Interactome3D": {
        "id": "url:https://interactome3d.irbbarcelona.org/",
        "type": "dataset",
        "title": "Interactome3D archived representative protein structure and model metadata",
        "url": "https://interactome3d.irbbarcelona.org/",
    },
    "ProBiS-Database": {
        "id": "url:http://probis.cmm.ki.si/?what=database",
        "type": "dataset",
        "title": "ProBiS-Database reference-chain catalog",
        "url": "http://probis.cmm.ki.si/?what=database",
    },
    "PDBTM": {
        "id": "url:https://pdbtm.unitmp.org/",
        "type": "dataset",
        "title": "PDBTM: Protein Data Bank of Transmembrane Proteins",
        "url": "https://pdbtm.unitmp.org/",
    },
    "3did": {
        "id": "url:https://3did.irbbarcelona.org/",
        "type": "dataset",
        "title": "3did: three-dimensional interacting domains",
        "url": "https://3did.irbbarcelona.org/",
    },
    "HPO": {
        "id": "url:https://hpo.jax.org/",
        "type": "dataset",
        "title": "Human Phenotype Ontology",
        "url": "https://hpo.jax.org/",
    },
    "MEROPS": {
        "id": "url:https://www.ebi.ac.uk/merops/",
        "type": "dataset",
        "title": "MEROPS: the peptidase database",
        "url": "https://www.ebi.ac.uk/merops/",
    },
    "MetalPDB": {
        "id": "url:https://metalpdb.cerm.unifi.it/",
        "type": "dataset",
        "title": "MetalPDB: metal sites in biological macromolecular structures",
        "url": "https://metalpdb.cerm.unifi.it/",
    },
    "ECOD": {
        "id": "url:http://prodata.swmed.edu/ecod/",
        "type": "dataset",
        "title": "ECOD: Evolutionary Classification of Protein Domains",
        "url": "http://prodata.swmed.edu/ecod/",
    },
    "TCDB": {
        "id": "url:https://tcdb.org/",
        "type": "dataset",
        "title": "Transporter Classification Database",
        "url": "https://tcdb.org/",
    },
    "ChannelsDB": {
        "id": "doi:10.1093/nar/gkad1012",
        "type": "article",
        "title": "ChannelsDB 2.0: a comprehensive database of protein tunnels and pores in AlphaFold era",
        "year": 2024,
        "journal": "Nucleic Acids Research",
        "volume": "52",
        "number": "D1",
        "pages": "D413–D418",
        "doi": "10.1093/nar/gkad1012",
        "url": "https://doi.org/10.1093/nar/gkad1012",
    },
    "SIGNOR": {
        "id": "url:https://signor.uniroma2.it/",
        "type": "dataset",
        "title": "SIGNOR: the Signaling Network Open Resource",
        "url": "https://signor.uniroma2.it/",
    },
    "APPRIS": {
        "id": "url:https://appris.bioinfo.cnio.es/",
        "type": "dataset",
        "title": "APPRIS: annotations of alternative splice isoforms",
        "url": "https://appris.bioinfo.cnio.es/",
    },
    "Complex Portal": {
        "id": "url:https://www.ebi.ac.uk/complexportal/",
        "type": "dataset",
        "title": "Complex Portal: an encyclopaedia of macromolecular complexes",
        "url": "https://www.ebi.ac.uk/complexportal/",
    },
    "CATH": {
        "id": "url:https://www.cathdb.info/",
        "type": "dataset",
        "title": "CATH: Protein Structure Classification Database",
        "url": "https://www.cathdb.info/",
    },
    "SWISS-MODEL Repository": {
        "id": "doi:10.1093/nar/gkw1132",
        "type": "article",
        "title": "The SWISS-MODEL Repository - new features and functionality",
        "authors": [
            "Bienert, S",
            "Waterhouse, A",
            "de Beer, TAP",
            "Tauriello, G",
            "Studer, G",
            "Bordoli, L",
            "Schwede, T",
        ],
        "year": 2017,
        "journal": "Nucleic Acids Research",
        "volume": "45",
        "number": "D1",
        "pages": "D313–D319",
        "doi": "10.1093/nar/gkw1132",
        "url": "https://doi.org/10.1093/nar/gkw1132",
    },
    "SWISS-MODEL": {
        "id": "doi:10.1093/nar/gky427",
        "type": "article",
        "title": "SWISS-MODEL: homology modelling of protein structures and complexes",
        "authors": [
            "Waterhouse, A",
            "Bertoni, M",
            "Bienert, S",
            "Studer, G",
            "Tauriello, G",
            "Gumienny, R",
            "Heer, FT",
            "de Beer, TAP",
            "Rempfer, C",
            "Bordoli, L",
            "Lepore, R",
            "Schwede, T",
        ],
        "year": 2018,
        "journal": "Nucleic Acids Research",
        "volume": "46",
        "number": "W1",
        "pages": "W296–W303",
        "doi": "10.1093/nar/gky427",
        "url": "https://doi.org/10.1093/nar/gky427",
    },
    "AmyPro": {
        "id": "doi:10.1093/nar/gkx950",
        "type": "article",
        "title": "AmyPro: a database of proteins with validated amyloidogenic regions",
        "authors": ["Varadi, M", "De Baets, G", "Vranken, WF", "Tompa, P", "Pancsa, R"],
        "year": 2018,
        "journal": "Nucleic Acids Research",
        "volume": "46",
        "number": "D1",
        "pages": "D387–D392",
        "doi": "10.1093/nar/gkx950",
        "url": "https://doi.org/10.1093/nar/gkx950",
    },
    "IntAct": {
        "id": "url:https://www.ebi.ac.uk/intact/",
        "type": "dataset",
        "title": "IntAct molecular interaction database",
        "url": "https://www.ebi.ac.uk/intact/",
    },
    "AlphaFill": {
        "id": "doi:10.1038/s41592-022-01685-y",
        "type": "article",
        "title": "AlphaFill: enriching AlphaFold models with ligands and cofactors",
        "authors": ["Hekkelman, ML", "de Vries, I", "Joosten, RP", "Perrakis, A"],
        "year": 2023,
        "journal": "Nature Methods",
        "volume": "20",
        "pages": "205–213",
        "doi": "10.1038/s41592-022-01685-y",
        "url": "https://doi.org/10.1038/s41592-022-01685-y",
    },
    "LIGYSIS": {
        "id": "url:https://www.compbio.dundee.ac.uk/ligysis/about",
        "type": "dataset",
        "title": "LIGYSIS: ligand binding site analysis resource",
        "url": "https://www.compbio.dundee.ac.uk/ligysis/about",
    },
    "GlyGen": {
        "id": "url:https://www.glygen.org/",
        "type": "dataset",
        "title": "GlyGen: computational and informatics resources for glycoscience",
        "url": "https://www.glygen.org/",
    },
    "EPPIC": {
        "id": "doi:10.1371/journal.pcbi.1006104",
        "type": "article",
        "title": "Automated evaluation of quaternary structures from protein crystals",
        "authors": ["Bliven, S", "Lafita, A", "Parker, A", "Capitani, G", "Duarte, JM"],
        "year": 2018,
        "journal": "PLoS Computational Biology",
        "volume": "14",
        "number": "4",
        "pages": "e1006104",
        "doi": "10.1371/journal.pcbi.1006104",
        "url": "https://doi.org/10.1371/journal.pcbi.1006104",
    },
    "PDB-REDO": {
        "id": "url:https://pdb-redo.eu/",
        "type": "dataset",
        "title": "PDB-REDO databank: re-refined and rebuilt crystallographic structures",
        "url": "https://pdb-redo.eu/",
    },
    "PDBe Validation": {
        "id": "url:https://www.ebi.ac.uk/pdbe/api/",
        "type": "dataset",
        "title": "PDBe API: entry-wide validation metrics and percentiles",
        "url": "https://www.ebi.ac.uk/pdbe/api/",
    },
    "SIFTS": {
        "id": "url:https://www.ebi.ac.uk/pdbe/docs/sifts/",
        "type": "dataset",
        "title": "SIFTS: Structure Integration with Function, Taxonomy and Sequence",
        "url": "https://www.ebi.ac.uk/pdbe/docs/sifts/",
    },
    "MobiDB": {
        "id": "url:https://mobidb.org/",
        "type": "dataset",
        "title": "MobiDB: a database of protein disorder and mobility annotations",
        "url": "https://mobidb.org/",
    },
    "AlphaMissense": {
        "id": "doi:10.1126/science.adg7492",
        "type": "article",
        "title": "Accurate proteome-wide missense variant effect prediction with AlphaMissense",
        "authors": [
            "Cheng, Jun",
            "Novati, Guido",
            "Pan, Joshua",
            "Bycroft, Clare",
            "Žemgulytė, Akvilė",
            "Applebaum, Taylor",
            "Pritzel, Alexander",
            "Wong, Lai Hong",
            "Zielinski, Michal",
            "Sargeant, Tobias",
            "Schneider, Rosalia G.",
            "Senior, Andrew W.",
            "Jumper, John",
            "Hassabis, Demis",
            "Kohli, Pushmeet",
            "Avsec, Žiga",
        ],
        "year": 2023,
        "journal": "Science",
        "doi": "10.1126/science.adg7492",
        "url": "https://www.science.org/doi/10.1126/science.adg7492",
    },
    "UniParc": {
        "id": "https://www.uniprot.org/help/uniparc",
        "type": "dataset",
        "title": "UniParc: UniProt Archive of protein sequences",
        "authors": [{"literal": "The UniProt Consortium"}],
        "url": "https://www.uniprot.org/help/uniparc",
    },
    "DisProt": {
        "id": "url:https://disprot.org/",
        "type": "dataset",
        "title": "DisProt: Database of Intrinsically Disordered Proteins",
        "url": "https://disprot.org/",
    },
    "AAindex": {
        "id": "url:https://www.genome.jp/aaindex/",
        "type": "dataset",
        "title": "AAindex: Amino Acid Index Database",
        "url": "https://www.genome.jp/aaindex/",
    },
    "ClinicalTrials.gov": {
        "id": "url:https://clinicaltrials.gov/",
        "type": "dataset",
        "title": "ClinicalTrials.gov",
        "url": "https://clinicaltrials.gov/",
        "note": "Source: National Library of Medicine. Native API/data timestamps and registry update dates remain source-access context, not publication years or permission for linked publications.",
    },
    "DISEASES": {
        "id": "doi:10.1093/database/baac019",
        "type": "article",
        "title": "Diseases 2.0: a weekly updated database of disease–gene associations from text mining and data integration",
        "authors": [
            "Grissa, Dhouha",
            "Junge, Alexander",
            "Oprea, Tudor I",
            "Jensen, Lars Juhl",
        ],
        "year": 2022,
        "journal": "Database",
        "volume": "2022",
        "pages": "baac019",
        "doi": "10.1093/database/baac019",
        "url": "https://doi.org/10.1093/database/baac019",
    },
    "ClinVar": {
        "id": "doi:10.1093/nar/gkt1113",
        "type": "article",
        "title": "ClinVar: public archive of relationships among sequence variation and human phenotype",
        "authors": [
            "Landrum, MJ",
            "Lee, JM",
            "Riley, GR",
            "Jang, W",
            "Rubinstein, WS",
            "Church, DM",
            "Maglott, DR",
        ],
        "year": 2014,
        "journal": "Nucleic Acids Research",
        "volume": "42",
        "number": "D1",
        "pages": "D980-D985",
        "doi": "10.1093/nar/gkt1113",
        "url": "https://doi.org/10.1093/nar/gkt1113",
    },
    "MedGen": {
        "id": "url:https://www.ncbi.nlm.nih.gov/medgen",
        "type": "dataset",
        "title": "MedGen",
        "authors": [
            {
                "literal": "National Library of Medicine (US), National Center for Biotechnology Information"
            }
        ],
        "year": 2012,
        "url": "https://www.ncbi.nlm.nih.gov/medgen",
        "note": "NCBI's recommended resource citation; database lastupdate and original access dates are separate source-access context.",
    },
    "Open Targets": {
        "id": "doi:10.1093/nar/gkae1128",
        "type": "article",
        "title": "Open Targets Platform: facilitating therapeutic hypotheses building in drug discovery",
        "authors": [
            "Buniello, Annalisa",
            "Suveges, Daniel",
            "Cruz-Castillo, Carlos",
            "Llinares, Manuel Bernal",
            "Cornu, Helena",
            "Lopez, Irene",
            "Tsukanov, Kirill",
            "Roldán-Romero, Juan María",
            "Mehta, Chintan",
            "Fumis, Luca",
            "McNeill, Graham",
            "Hayhurst, James D",
            "Martinez Osorio, Ricardo Esteban",
            "Barkhordari, Ehsan",
            "Ferrer, Javier",
            "Carmona, Miguel",
            "Uniyal, Prashant",
            "Falaguera, Maria J",
            "Rusina, Polina",
            "Smit, Ines",
            "Schwartzentruber, Jeremy",
            "Alegbe, Tobi",
            "Ho, Vivien W",
            "Considine, Daniel",
            "Ge, Xiangyu",
            "Szyszkowski, Szymon",
            "Tsepilov, Yakov",
            "Ghoussaini, Maya",
            "Dunham, Ian",
            "Hulcoop, David G",
            "McDonagh, Ellen M",
            "Ochoa, David",
        ],
        "year": 2025,
        "journal": "Nucleic Acids Research",
        "volume": "53",
        "number": "D1",
        "pages": "D1467-D1475",
        "doi": "10.1093/nar/gkae1128",
        "url": "https://doi.org/10.1093/nar/gkae1128",
    },
    "Orphanet": {
        "id": "url:https://sciences.orphadata.com",
        "type": "dataset",
        "title": "Orphadata Science: Free access data from Orphanet",
        "authors": ["INSERM"],
        "url": "https://sciences.orphadata.com",
        "note": "Native file date and original access are retained in source-access context; copyright 1999 is not a publication date.",
    },
    "MONDO": {
        "id": "doi:10.1093/genetics/iyaf215",
        "type": "article",
        "title": "Mondo: integrating disease terminology across communities",
        "authors": [
            "Vasilevsky, Nicole A",
            "Toro, Sabrina",
            "Matentzoglu, Nicolas",
            "Flack, Joseph E",
            "Mullen, Kathleen R",
            "Hegde, Harshad",
            "Gehrke, Sarah",
            "Whetzel, Patricia L",
            "Shwetar, Yousif",
            "Harris, Nomi L",
            "Ngu, Mee S",
            "Alyea, Gioconda L",
            "Kane, Megan S",
            "Roncaglia, Paola",
            "Sid, Eric",
            "Thaxton, Courtney L",
            "Wood, Valerie",
            "Abraham, Roshini S",
            "Achatz, Maria Isabel",
            "Ajuyah, Pamela",
            "Amberger, Joanna S",
            "Babb, Lawrence",
            "Baker, Jasmine",
            "Balhoff, James P",
            "Berg, Jonathan S",
            "Bhalla, Amol",
            "Bofill-De Ros, Xavier",
            "Braun, Ian R",
            "Broeren, Eleanor C",
            "Byer, Blake K",
            "Byrne, Alicia B",
            "Callahan, Tiffany J",
            "Carmody, Leigh C",
            "Chan, Lauren E",
            "Clause, Amanda R",
            "Cohen, Julie S",
            "DeLuca, Marcello",
            "Deuitch, Natalie T",
            "Flowers, May",
            "Fraser, Jamie",
            "Fujiwara, Toyofumi",
            "Gitau, Vanessa",
            "Goldstein, Jennifer L",
            "Gration, Dylan",
            "Groza, Tudor",
            "Gyori, Benjamin M",
            "Hankey, William",
            "Hilton, Jason A",
            "Himmelstein, Daniel S",
            "Hong, Stephanie S",
            "Hoyt, Charles T",
            "Huether, Robert",
            "Hurwitz, Eric",
            "Jacobsen, Julius O B",
            "Kikuchi, Atsuo",
            "Köhler, Sebastian",
            "Korn, Daniel R",
            "Lagorce, David",
            "Laraway, Bryan J",
            "Li, Jane Y",
            "Malheiro, Adriana J",
            "McLaughlin, James",
            "Meldal, Birgit H M",
            "Mohan, Shruthi",
            "Moxon, Sierra A T",
            "Munoz-Torres, Monica C",
            "Nelson, Tristan H",
            "Nicholas, Frank W",
            "Ochoa, David",
            "Olson, Daniel",
            "Oprea, Tudor I",
            "Oskotsky, Tomiko T",
            "Osumi-Sutherland, David",
            "Paris, Kelley",
            "Parkinson, Helen E",
            "Pendlington, Zoë M",
            "Peng, Xiao P",
            "Pizzino, Amy",
            "Plon, Sharon E",
            "Powell, Bradford C",
            "Ratliff, Julie C",
            "Rehm, Heidi L",
            "Remennik, Lyubov",
            "Riggs, Erin R",
            "Roberts, Sean",
            "Robinson, Peter N",
            "Ross, Justyne E",
            "Schaper, Kevin",
            "Schilder, Brian M",
            "Schmidt, Johanna L",
            "Sharp, Elliott W",
            "Similuk, Morgan N",
            "Smedley, Damian",
            "Sneddon, Tam P",
            "Sparks, Rachel",
            "Stefancsik, Ray",
            "Stupp, Gregory S",
            "Sundar, Shilpa",
            "Takatsuki, Terue",
            "Tammen, Imke",
            "Tshering, Kezang C",
            "Unni, Deepak R",
            "Valasek, Eloise",
            "Vanderver, Adeline",
            "Wagner, Alex H",
            "Webb, Ryan F",
            "Welter, Danielle",
            "Yaya-Stupp, Doron",
            "Zankl, Andreas",
            "Zhang, Xingmin Aaron",
            "McMurry, Julie A",
            "Chute, Christopher G",
            "Hamosh, Ada",
            "Mungall, Christopher J",
            "Haendel, Melissa A",
        ],
        "year": 2026,
        "journal": "Genetics",
        "volume": "232",
        "number": "4",
        "pages": "iyaf215",
        "doi": "10.1093/genetics/iyaf215",
        "url": "https://doi.org/10.1093/genetics/iyaf215",
    },
    "InterPro": {
        "id": "doi:10.1093/nar/gkae1082",
        "type": "article",
        "title": "InterPro: the protein sequence classification resource in 2025",
        "authors": [
            "Blum, Matthias",
            "Andreeva, Antonina",
            "Florentino, Laise Cavalcanti",
            "Chuguransky, Sara Rocio",
            "Grego, Tiago",
            "Hobbs, Emma",
            "Pinto, Beatriz Lazaro",
            "Orr, Ailsa",
            "Paysan-Lafosse, Typhaine",
            "Ponamareva, Irina",
            "Salazar, Gustavo A",
            "Bordin, Nicola",
            "Bork, Peer",
            "Bridge, Alan",
            "Colwell, Lucy",
            "Gough, Julian",
            "Haft, Daniel H",
            "Letunic, Ivica",
            "Llinares-López, Felipe",
            "Marchler-Bauer, Aron",
            "Meng-Papaxanthos, Laetitia",
            "Mi, Huaiyu",
            "Natale, Darren A",
            "Orengo, Christine A",
            "Pandurangan, Arun P",
            "Piovesan, Damiano",
            "Rivoire, Catherine",
            "Sigrist, Christian J A",
            "Thanki, Narmada",
            "Thibaud-Nissen, Françoise",
            "Thomas, Paul D",
            "Tosatto, Silvio C E",
            "Wu, Cathy H",
            "Bateman, Alex",
        ],
        "year": 2025,
        "journal": "Nucleic Acids Research",
        "volume": "53",
        "number": "D1",
        "pages": "D444-D456",
        "doi": "10.1093/nar/gkae1082",
        "url": "https://doi.org/10.1093/nar/gkae1082",
    },
    "PDBe-KB": {
        "id": "doi:10.1093/nar/gkab988",
        "type": "article",
        "title": "PDBe-KB: collaboratively defining the biological context of structural data",
        "authors": [{"literal": "PDBe-KB consortium"}],
        "year": 2022,
        "journal": "Nucleic Acids Research",
        "volume": "50",
        "number": "D1",
        "pages": "D534-D542",
        "doi": "10.1093/nar/gkab988",
        "url": "https://doi.org/10.1093/nar/gkab988",
    },
    "PDB CCD": {
        "id": "doi:10.1093/bioinformatics/btu789",
        "type": "article",
        "title": "The chemical component dictionary: complete descriptions of constituent molecules in experimentally determined 3D macromolecules in the Protein Data Bank",
        "authors": [
            "Westbrook, John D",
            "Shao, Chenghua",
            "Feng, Zukang",
            "Zhuravleva, Marina",
            "Velankar, Sameer",
            "Young, Jasmine",
        ],
        "year": 2015,
        "journal": "Bioinformatics",
        "volume": "31",
        "number": "8",
        "pages": "1274-1278",
        "doi": "10.1093/bioinformatics/btu789",
        "url": "https://doi.org/10.1093/bioinformatics/btu789",
    },
    "UniChem": {
        "id": "doi:10.1186/1758-2946-5-3",
        "type": "article",
        "title": "UniChem: a unified chemical structure cross-referencing and identifier tracking system",
        "authors": [
            "Chambers, Jon",
            "Davies, Mark",
            "Gaulton, Anna",
            "Hersey, Anne",
            "Velankar, Sameer",
            "Petryszak, Robert",
            "Hastings, Janna",
            "Bellis, Louisa",
            "McGlinchey, Shaun",
            "Overington, John P",
        ],
        "year": 2013,
        "journal": "Journal of Cheminformatics",
        "volume": "5",
        "number": "1",
        "pages": "3",
        "doi": "10.1186/1758-2946-5-3",
        "url": "https://doi.org/10.1186/1758-2946-5-3",
    },
    "BindingDB": {
        "id": "doi:10.1093/nar/gkae1075",
        "type": "article",
        "title": "BindingDB in 2024: a FAIR knowledgebase of protein-small molecule binding data",
        "authors": [
            "Liu, Tiqing",
            "Hwang, Linda",
            "Burley, Stephen K",
            "Nitsche, Carmen I",
            "Southan, Christopher",
            "Walters, W Patrick",
            "Gilson, Michael K",
        ],
        "year": 2025,
        "journal": "Nucleic Acids Research",
        "volume": "53",
        "number": "D1",
        "pages": "D1633-D1644",
        "doi": "10.1093/nar/gkae1075",
        "url": "https://doi.org/10.1093/nar/gkae1075",
    },
    "PubChem": {
        "id": "doi:10.1093/nar/gkae1059",
        "type": "article",
        "title": "PubChem 2025 update",
        "authors": [
            "Kim, Sunghwan",
            "Chen, Jie",
            "Cheng, Tiejun",
            "Gindulyte, Asta",
            "He, Jia",
            "He, Siqian",
            "Li, Qingliang",
            "Shoemaker, Benjamin A",
            "Thiessen, Paul A",
            "Yu, Bo",
            "Zaslavsky, Leonid",
            "Zhang, Jian",
            "Bolton, Evan E",
        ],
        "year": 2025,
        "journal": "Nucleic Acids Research",
        "volume": "53",
        "number": "D1",
        "pages": "D1516-D1525",
        "doi": "10.1093/nar/gkae1059",
        "url": "https://doi.org/10.1093/nar/gkae1059",
    },
    "ChEMBL": {
        "id": "doi:10.1093/nar/gkad1004",
        "type": "article",
        "title": "The ChEMBL Database in 2023: a drug discovery platform spanning multiple bioactivity data types and time periods",
        "authors": [
            "Zdrazil, B",
            "Felix, E",
            "Hunter, F",
            "Manners, EJ",
            "Blackshaw, J",
            "Corbett, S",
            "de Veij, M",
            "Ioannidis, H",
            "Lopez, DM",
            "Mosquera, JF",
            "Magarinos, MP",
            "Bosc, N",
            "Arcila, R",
            "Kizilören, T",
            "Gaulton, A",
            "Bento, AP",
            "Adasme, MF",
            "Monecke, P",
            "Landrum, GA",
            "Leach, AR",
        ],
        "year": 2024,
        "journal": "Nucleic Acids Research",
        "volume": "52",
        "number": "D1",
        "pages": "D1180-D1192",
        "doi": "10.1093/nar/gkad1004",
        "url": "https://doi.org/10.1093/nar/gkad1004",
    },
    "UniProt": {
        "id": "doi:10.1093/nar/gkae1010",
        "type": "article",
        "title": "UniProt: the Universal Protein Knowledgebase in 2025",
        "authors": [{"literal": "The UniProt Consortium"}],
        "year": 2025,
        "journal": "Nucleic Acids Research",
        "volume": "53",
        "number": "D1",
        "pages": "D609-D617",
        "doi": "10.1093/nar/gkae1010",
        "url": "https://doi.org/10.1093/nar/gkae1010",
    },
    "Europe PMC": {
        "id": "doi:10.1093/nar/gkad1085",
        "type": "article",
        "title": "Europe PMC in 2023",
        "authors": [
            "Rosonovski, Summer",
            "Levchenko, Maria",
            "Bhatnagar, Rajat",
            "Chandrasekaran, Umamageswari",
            "Faulk, Lynne",
            "Hassan, Islam",
            "Jeffryes, Matt",
            "Mubashar, Syed Irtaza",
            "Nassar, Maaly",
            "Palanisamy, Madhumiethaa Jayaprabha",
            "Parkin, Michael",
            "Poluru, Jagadeeswararao",
            "Rogers, Frances",
            "Saha, Shyamasree",
            "Selim, Mohamed",
            "Shafique, Zunaira",
            "Ide-Smith, Michele",
            "Stephenson, David",
            "Tirunagari, Santosh",
            "Venkatesan, Aravind",
            "Xing, Lijun",
            "Harrison, Melissa",
        ],
        "year": 2024,
        "journal": "Nucleic Acids Research",
        "volume": "52",
        "number": "D1",
        "pages": "D1668-D1676",
        "doi": "10.1093/nar/gkad1085",
        "url": "https://doi.org/10.1093/nar/gkad1085",
    },
    "RCSB PDB": {
        "id": "doi:10.1093/nar/gkae1091",
        "type": "article",
        "title": "Updated resources for exploring experimentally-determined PDB structures and Computed Structure Models at the RCSB Protein Data Bank",
        "authors": [
            "Burley, Stephen K",
            "Bhatt, Rusham",
            "Bhikadiya, Charmi",
            "Bi, Chunxiao",
            "Biester, Alison",
            "Biswas, Pratyoy",
            "Bittrich, Sebastian",
            "Blaumann, Santiago",
            "Brown, Ronald",
            "Chao, Henry",
            "Chithari, Vivek Reddy",
            "Craig, Paul A",
            "Crichlow, Gregg V",
            "Duarte, Jose M",
            "Dutta, Shuchismita",
            "Feng, Zukang",
            "Flatt, Justin W",
            "Ghosh, Sutapa",
            "Goodsell, David S",
            "Green, Rachel Kramer",
            "Guranovic, Vladimir",
            "Henry, Jeremy",
            "Hudson, Brian P",
            "Joy, Michael",
            "Kaelber, Jason T",
            "Khokhriakov, Igor",
            "Lai, Jhih-Siang",
            "Lawson, Catherine L",
            "Liang, Yuhe",
            "Myers-Turnbull, Douglas",
            "Peisach, Ezra",
            "Persikova, Irina",
            "Piehl, Dennis W",
            "Pingale, Aditya",
            "Rose, Yana",
            "Sagendorf, Jared",
            "Sali, Andrej",
            "Segura, Joan",
            "Sekharan, Monica",
            "Shao, Chenghua",
            "Smith, James",
            "Trumbull, Michael",
            "Vallat, Brinda",
            "Voigt, Maria",
            "Webb, Ben",
            "Whetstone, Shamara",
            "Wu-Wu, Amy",
            "Xing, Tongji",
            "Young, Jasmine Y",
            "Zalevsky, Arthur",
            "Zardecki, Christine",
        ],
        "year": 2025,
        "journal": "Nucleic Acids Research",
        "volume": "53",
        "number": "D1",
        "pages": "D564-D574",
        "doi": "10.1093/nar/gkae1091",
        "url": "https://doi.org/10.1093/nar/gkae1091",
    },
}


_ALPHAFOLD_DESCRIPTIONS = [
    {
        "id": "doi:10.1093/nar/gkad1011",
        "type": "article",
        "title": "AlphaFold Protein Structure Database in 2024: providing structure coverage "
        "for over 214 million protein sequences",
        "authors": [
            "Varadi, Mihaly",
            "Bertoni, Damian",
            "Magana, Paulyna",
            "Paramval, Urmila",
            "Pidruchna, Ivanna",
            "Radhakrishnan, Malarvizhi",
            "Tsenkov, Maxim",
            "Nair, Sreenath",
            "Mirdita, Milot",
            "Yeo, Jingi",
            "Kovalevskiy, Oleg",
            "Tunyasuvunakool, Kathryn",
            "Laydon, Agata",
            "Žídek, Augustin",
            "Tomlinson, Hamish",
            "Hariharan, Dhavanthi",
            "Abrahamson, Josh",
            "Green, Tim",
            "Jumper, John",
            "Birney, Ewan",
            "Steinegger, Martin",
            "Hassabis, Demis",
            "Velankar, Sameer",
        ],
        "year": 2024,
        "journal": "Nucleic Acids Research",
        "volume": "52",
        "number": "D1",
        "pages": "D368-D375",
        "doi": "10.1093/nar/gkad1011",
        "url": "https://doi.org/10.1093/nar/gkad1011",
    },
    {
        "id": "doi:10.1093/nar/gkab1061",
        "type": "article",
        "title": "AlphaFold Protein Structure Database: massively expanding the structural "
        "coverage of protein-sequence space with high-accuracy models",
        "authors": [
            "Varadi, Mihaly",
            "Anyango, Stephen",
            "Deshpande, Mandar",
            "Nair, Sreenath",
            "Natassia, Cindy",
            "Yordanova, Galabina",
            "Yuan, David",
            "Stroe, Oana",
            "Wood, Gemma",
            "Laydon, Agata",
            "Žídek, Augustin",
            "Green, Tim",
            "Tunyasuvunakool, Kathryn",
            "Petersen, Stig",
            "Jumper, John",
            "Clancy, Ellen",
            "Green, Richard",
            "Vora, Ankur",
            "Lutfi, Mira",
            "Figurnov, Michael",
            "Cowie, Andrew",
            "Hobbs, Nicole",
            "Kohli, Pushmeet",
            "Kleywegt, Gerard",
            "Birney, Ewan",
            "Hassabis, Demis",
            "Velankar, Sameer",
        ],
        "year": 2022,
        "journal": "Nucleic Acids Research",
        "volume": "50",
        "number": "D1",
        "pages": "D439-D444",
        "doi": "10.1093/nar/gkab1061",
        "url": "https://doi.org/10.1093/nar/gkab1061",
    },
    {
        "id": "doi:10.1038/s41586-021-03819-2",
        "type": "article",
        "title": "Highly accurate protein structure prediction with AlphaFold",
        "authors": [
            "Jumper, John",
            "Evans, Richard",
            "Pritzel, Alexander",
            "Green, Tim",
            "Figurnov, Michael",
            "Ronneberger, Olaf",
            "Tunyasuvunakool, Kathryn",
            "Bates, Russ",
            "Žídek, Augustin",
            "Potapenko, Anna",
            "Bridgland, Alex",
            "Meyer, Clemens",
            "Kohl, Simon A. A.",
            "Ballard, Andrew J.",
            "Cowie, Andrew",
            "Romera-Paredes, Bernardino",
            "Nikolov, Stanislav",
            "Jain, Rishub",
            "Adler, Jonas",
            "Back, Trevor",
            "Petersen, Stig",
            "Reiman, David",
            "Clancy, Ellen",
            "Zielinski, Michal",
            "Steinegger, Martin",
            "Pacholska, Michalina",
            "Berghammer, Tamas",
            "Bodenstein, Sebastian",
            "Silver, David",
            "Vinyals, Oriol",
            "Senior, Andrew W.",
            "Kavukcuoglu, Koray",
            "Kohli, Pushmeet",
            "Hassabis, Demis",
        ],
        "year": 2021,
        "journal": "Nature",
        "volume": "596",
        "number": "7873",
        "pages": "583-589",
        "doi": "10.1038/s41586-021-03819-2",
        "url": "https://doi.org/10.1038/s41586-021-03819-2",
    },
]


def descriptions(source):
    if source == "AlphaFold DB":
        return deepcopy(_ALPHAFOLD_DESCRIPTIONS)
    item = _DESCRIPTIONS.get("PubChem" if source == "PubChem BioAssay" else source)
    items = [item] if item else []
    if source in {"gnomAD", "GTEx"}:
        from .comparative_bibliography import resource_descriptions

        items = [*resource_descriptions(source), *items]
    if source == "PDB CCD":
        # CCD defines the data; RCSB distributes it through the queried API.
        items.append(_DESCRIPTIONS["RCSB PDB"])
    if source == "SWISS-MODEL Repository":
        items.append(_DESCRIPTIONS["SWISS-MODEL"])
    return deepcopy(items)


def pubchem_citations(publication_ids):
    """PubMed pointers remain incomplete citations, never DOI/name enriched."""
    from .snapshot import canonical_json, digest

    citations, gaps = [], []
    for pubmed in publication_ids:
        # A source-stated pointer cannot overwrite a fuller citation already used
        # by the host under its publication identifier.
        identifier = "sabueso:pubchem-primary-citation:" + digest(
            canonical_json({"pubmed_id": pubmed})
        )
        citations.append(
            {
                "id": identifier,
                "type": "article",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pubmed}/",
            }
        )
        gaps.append(
            {
                "publication_ref": "pubmed:" + pubmed,
                "citation_id": identifier,
                "reason": "measurement_citation_metadata_not_stated",
                "fields": ["title", "authors", "year"],
            }
        )
    return citations, gaps


def bindingdb_citations(publications):
    """Retain native DOI/PubMed forms without replacing fuller host citations."""
    from .snapshot import canonical_json, digest

    citations, gaps = [], []
    for publication in publications:
        identifier = "sabueso:bindingdb-primary-citation:" + digest(
            canonical_json(publication)
        )
        item = {"id": identifier, "type": "article"}
        if publication.get("doi"):
            item.update(
                doi=deepcopy(publication["doi"]),
                url="https://doi.org/" + str(publication["doi"]),
            )
        elif publication.get("pmid"):
            item["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{publication['pmid']}/"
        citations.append(item)
        gaps.append(
            {
                "publication": deepcopy(publication),
                "citation_id": identifier,
                "reason": "measurement_citation_metadata_not_stated",
                "fields": ["title", "authors", "year"],
            }
        )
    return citations, gaps


def chembl_citations(documents):
    """Original document forms remain distinct; missing authors are never inferred."""
    from .snapshot import canonical_json, digest

    citations, gaps = [], []
    for document_id, document in sorted(documents.items()):
        identifier = "sabueso:chembl-document-citation:" + digest(
            canonical_json(document)
        )
        item = {"id": identifier, "type": "article"}
        for key in ("title", "year", "journal", "doi"):
            if document.get(key):
                item[key] = deepcopy(document[key])
        if document.get("doi"):
            item["url"] = "https://doi.org/" + document["doi"]
        elif document.get("pubmed_id"):
            item["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{document['pubmed_id']}/"
        gaps.append(
            {
                "document_id": document_id,
                "citation_id": identifier,
                "reason": "document_citation_metadata_not_stated",
                "fields": [
                    key for key in ("title", "authors", "year") if not item.get(key)
                ],
            }
        )
        citations.append(item)
    return citations, gaps


def structure_citations(entries):
    """Preserve only primary publication metadata stated for received PDB entries.

    No DOI lookup supplies missing authors, title or date. Identical metadata is
    reused; different source-stated forms of a publication remain distinct. This
    prevents a partial citation from replacing a previous complete reference.
    """
    from .snapshot import canonical_json, digest

    citations, gaps = {}, []
    for entry in entries:
        if entry["outcome"] not in {"received", "partial"}:
            continue
        citation = entry.get("primary_citation") or {}
        if not citation:
            gaps.append(
                {"pdb_id": entry["pdb_id"], "reason": "primary_citation_not_stated"}
            )
            continue
        doi = citation.get("pdbx_database_id_DOI")
        pubmed = citation.get("pdbx_database_id_PubMed")
        identifier = "sabueso:rcsb-primary-citation:" + digest(canonical_json(citation))
        item = {"id": identifier, "type": "article"}
        for source_key, target_key in (
            ("title", "title"),
            ("rcsb_authors", "authors"),
            ("year", "year"),
            ("journal_abbrev", "journal"),
            ("pdbx_database_id_DOI", "doi"),
        ):
            if citation.get(source_key):
                item[target_key] = deepcopy(citation[source_key])
        if doi:
            item["url"] = "https://doi.org/" + doi
        elif pubmed:
            item["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed}/"
        missing = [key for key in ("title", "authors", "year") if not item.get(key)]
        if missing:
            gaps.append(
                {
                    "pdb_id": entry["pdb_id"],
                    "citation_id": identifier,
                    "reason": "primary_citation_metadata_not_stated",
                    "fields": missing,
                }
            )
        citations[identifier] = item
    return list(citations.values()), gaps


def software():
    from sabueso import __version__

    return {
        "id": f"software:sabueso:{__version__}",
        "type": "software",
        "title": "Sabueso",
        "authors": ["Prada-Gracia, Diego", "Moreno-Vargas, Liliana M."],
        "version": __version__,
        # The concept DOI describes the project. Do not label an unreleased
        # checkout with the version-specific DOI of its preceding release.
        "doi": "10.5281/zenodo.22937375",
        "url": "https://github.com/uibcdf/sabueso",
    }
