
def load_document(file_path):
    """
    Load a document from the specified file path.

    Args:
        file_path (str): The path to the document file."""
    with open(file_path, "r") as f:
        text = f.read()
    return text
def chunks_text(text,chunk_size,overlap):
    """
    Split the input text into chunks based on newline characters.
    """
    chunks=[]
    step=chunk_size - overlap
    for i in range(0, len(text), step):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
        print("Start:", i)
        print("End:", i + chunk_size)
        print("Document length:", len(text))
        if i+chunk_size >= len(text):
            break
    return chunks
def chunk_paragraphs(text, chunk_size, overlap):
    """
    Split the input text into chunks based on paragraph breaks.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        if not paragraph:
            continue
        # Handle a paragraph that is too large on its own
        if len(paragraph) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            chunks.extend(split_long_paragraph(paragraph, chunk_size))
            continue
        seperator = "\n\n" if current_chunk else ""
        candidate=current_chunk + seperator + paragraph
        if len(candidate) <= chunk_size:
            current_chunk =candidate
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk=paragraph
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def split_long_paragraph(paragraph, max_size):
    pieces = []

    for start in range(0, len(paragraph), max_size):
        pieces.append(paragraph[start:start + max_size])

    return pieces


text = load_document(r"E:\Support-Docs-Copilot\documents\support-docs\password-policy.md")
print(text)


'''chunks = chunks_text(text, 100, 20)

print("Total chunks:", len(chunks))
for i, chunk in enumerate(chunks):
    print(f"chunk {i+1}:\n{chunk}\n")'''

chunks = chunk_paragraphs(text, 300, 20)

print("Total chunks:", len(chunks))



# Test 1: Your actual support document
chunks = chunk_paragraphs(text, 300,20)

print("Document chunks:", len(chunks))
print("Document chunk lengths:", [len(c) for c in chunks])

# Test 2: An oversized paragraph
long_text = "A" * 800
test_chunks = chunk_paragraphs(long_text, 300, 20)

print("Long-text chunks:", len(test_chunks))
print("Long-text chunk lengths:", [len(c) for c in test_chunks])

assert all(len(c) <= 300 for c in chunks)
assert all(len(c) <= 300 for c in test_chunks)