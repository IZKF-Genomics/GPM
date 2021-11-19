version_info = (0,2,0)
version = ".".join([str(c) for c in version_info])

APPLICATIONS = ["RNAseq", "totalRNAseq", "mRNAseq", "3mRNAseq",
                "ChIPseq", "ATACseq", "Ampseq",
                "scRNAseq",
                "WGS", "WES"]

EXPORT_URL = "https://genomics.rwth-aachen.de/data/"
SYMLINK_From_Web = "/mnt/nextgen3/"