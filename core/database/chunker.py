""""
This file is responsinble for chunking the content of the documents.
It is mainly created for chunking the properties files.


Currently, the chunker is not used.
This is because the property files have around 140 lines each. 
If the need arises, the chunker can be used.

"""


class DocumentChunker:
    def __init__(self):
        self.chunker = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "]
        )
    
    def chunk_document(self, document):
        pass
    