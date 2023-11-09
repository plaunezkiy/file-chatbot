import os
from pathlib import Path
from flask import Flask, request
from llama_index import SimpleDirectoryReader, VectorStoreIndex, StorageContext, download_loader, load_index_from_storage
from llama_index.readers.notion import NotionPageReader

os.environ["OPENAI_API_KEY"] = ""


app = Flask(__name__)
index = None
# index_dir = "index/"
index_dir = "pezze/"
# index_dir = "algos/"
# index_dir = "paper/"
# index_dir = "case/"


def initialize_index():
    global index
    if os.path.exists(index_dir):
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        index = load_index_from_storage(storage_context)
    else:
        storage_context = StorageContext.from_defaults()
        integration_token = os.getenv("NOTION_INTEGRATION_TOKEN")
        page_ids = ["ef7ac290-d07a-43d6-b65d-f6f8c426913c"]
        reader = NotionPageReader(integration_token=integration_token)
        documents = reader.load_data(page_ids=page_ids)
        # documents = SimpleDirectoryReader("./documents").load_data()
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )
        storage_context.persist(index_dir)
    # query_file()
    # PDFReader = download_loader("PDFReader")
    # loader = PDFReader()
    # documents = loader.load_data(file=Path('./case.pdf'))

    # storage_context = StorageContext.from_defaults()
    # index = VectorStoreIndex.from_documents(
    #         documents, storage_context=storage_context
    # )
    # storage_context.persist(index_dir)
    

def query_file():
    # query_text = "Summarize the topic of balanced trees ONLY using the information provided in the index. Provide details expanding on all mentioned terms and descriptions using appropriate mathematical notation"
    # query_text = "using ONLY the information provided in the context. Estimate the overall volume of the content present on the topic and devise a study plan for a third year university student over 10 days covering all details, concepts, and descriptions including mathematical notation. The plan should roughly include 3 hours of studying every day. Produce a list of days with detailed descriptions of what to cover on each day"
    # query_text = "ONLY using the information provided in the index, produce a highly detailed summary of the court case, what happened, who was involved and for what reason. Provide references to previous proceedings with details about them too"
    query_engine = index.as_query_engine()
    while True:
        query_text = input("Enter a prompt: ")
        response = query_engine.query("Only using the information provided in the index," + query_text)
        print(response)
    # print(dir(response.source_nodes[0]))


@app.route("/query", methods=["GET"])
def query_index():
    global index
    query_text = request.args.get("text", None)
    if query_text is None:
        return (
            "No text found, please include a ?text=blah parameter in the URL",
            400,
        )
    query_engine = index.as_query_engine()
    response = query_engine.query(query_text)
    # print(dir(response.source_nodes[0]), dir(response.source_nodes[0].node))
    response_json = {
        "text": str(response),
        "sources": [{"text": str(x.text), 
                     "similarity": round(x.score, 2),
                    #  "doc_id": str(x.id_),
                    #  "start": x.node_info['start'],
                    #  "end": x.node_info['end']
                    } for x in response.source_nodes]
    }
    return str(response_json), 200


if __name__ == "__main__":
    initialize_index()
    query_file()
    # app.run(host="0.0.0.0", port=5601)
