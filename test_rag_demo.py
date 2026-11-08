from app.rag.policy_rag import PolicyRAG

rag = PolicyRAG()

stats = rag.build_index()

print("Index statistics:", stats)

query = "Can I return an unused product?"

print("\nFULL DOCUMENT RESULTS")
for result in rag.search(query, strategy="full"):
    print(result)

print("\nSENTENCE CHUNK RESULTS")
for result in rag.search(query, strategy="chunks"):
    print(result)
