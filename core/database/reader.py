"""
This module is responsible for reading the content of the documents and splitting them into chunks.
It is mainly created for reading the properties files. 
"""

from langchain.document_loaders import TextLoader

# one class
# one method for reading only one filw
# one method for reading all files in a directory

class DocumentReader:
    def __init__(self):
        self.loader = TextLoader()
    
    def read_document(self, file_path):
        documents = self.loader.load(file_path)
        return documents
    
    def read_all_documents(self, directory_path):
        documents = []
        for file in os.listdir(directory_path):
            if file.endswith(".txt"):
                documents.append(self.read_document(os.path.join(directory_path, file)))
        return documents

def read_documents(file_path):
    loader = TextLoader(file_path)
    documents = loader.load()
    return documents

