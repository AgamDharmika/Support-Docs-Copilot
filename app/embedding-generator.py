from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


#step1: load the document
def load_document(file_path):
    with open(file_path,"r") as file:
        text=file.read()
    return text

#step2: split the document into chunks
def split_long_paragraph(paragraph,max_size):
    pieces=[]
    for start in range(0,len(paragraph),max_size):
        pieces.append(paragraph[start:start+max_size])
    return pieces

#step3: create document chunks based on paragraph breaks
def chunk_paragraphs(text,chunk_size):
    paragraphs=text.split("\n\n")
    chunks=[]
    current_chunk=""
    for paragraph in paragraphs:
        paragraph=paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph)>chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk=""
            chunks.extend(split_long_paragraph(paragraph,chunk_size))
            continue
        seperator="\n\n" if current_chunk else ""
        candidate=current_chunk + seperator + paragraph
        if len(candidate) <= chunk_size:
            current_chunk=candidate
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk=paragraph
    if current_chunk:
        chunks.append(current_chunk)
    return chunks



#step4: find the document path
project_root=Path(__file__).resolve().parent.parent
file_path=project_root/"documents"/"support-docs"/"password-policy.md"


#step5: load and chunk the document
text=load_document(file_path)
chunks=chunk_paragraphs(text,chunk_size=300)
print("total chunks:",len(chunks))
for index,chunk in enumerate(chunks):
    print(f"\nChunk {index+1}:\n {chunk}\n")


#step6: load embedding model
model=SentenceTransformer('all-MiniLM-L6-v2')

'''#sample text
sentences=[
    "Employees must change their password for every 90 days.",
    "when should i update my password",
    "how should i reset my forgotten password"
]'''

#step7: generate embeddings
embeddings=model.encode(chunks,show_progress_bar=True)
similarity_matrix=cosine_similarity(embeddings)


from pathlib import Path
import chromadb
#create a persistent ChromaDB instance
client=chromadb.PersistentClient(path=str(project_root/"chroma_db"))

#create or access a collection
collection=client.get_or_create_collection(
    name="support_documents",
    metadata={"hnsw:space":"cosine"}
)

#generate unique ids for document chunks
ids=[
    f"password-policy-chunk-{i+1:03d}" for i in range(len(chunks))
]

#Store source information of each chunk
metadatas=[
    {
        "source":"password-policy.md",
        "chunk_index":i
    }
    for i in range(len(chunks))
]

# Store chunks,embeddings, and metadate
collection.upsert(
    ids=ids,
    documents=chunks,
    embeddings=embeddings.tolist(),
    metadatas=metadatas
)

stored_data=collection.get(
    include=["documents","metadatas","embeddings"]
)

#dispaly results
print("Embeddings:", embeddings)
print("Shape of embeddings:",embeddings.shape)
print("Similarity Matrix:", similarity_matrix)

print("Number of chunks:", len(chunks))
print("Number of vectors:", len(embeddings))
print("Values in first vector:", len(embeddings[0]))

print("First 10 values:", embeddings[0][:10])

#printing documents stored in vector database
print("Documents stored successfully")
print("Total records:",collection.count())

print("\nStored documents:")
print(stored_data)
print("Embedding shape:", stored_data["embeddings"].shape)