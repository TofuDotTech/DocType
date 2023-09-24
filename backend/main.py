from flask import Flask, request
from softtek_llm.schemas import Vector
from fridaConfig import embeddings_model, vector_store, chatbot
import wikipedia
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
wikipedia.set_lang("es")

@app.route("/api/doctor", methods=["POST"])
def doctorPost():
    json = request.json
    query = json["query"]
    query_vector = Vector(embeddings=embeddings_model.embed(query), id=query)
    search_vectors = vector_store.search(query_vector, top_k=3)
    res_dic = {
        'results': []
    }
    evaluation = vector.metadata["evaluation"]
    treatment = vector.metadata["treatment"]
    evaluation_response = chatbot.chat(
        "Resume la siguiente evaluación de un paciente para un médico: " + evaluation
    )
    treatment_response = chatbot.chat(
        "Resume el siguiente tratamiento que se le dio a un paciente para un médico: " + treatment
    )
    for vector in search_vectors:
        temp = {
            "id": vector.id,
            "evaluation": evaluation_response.message.content,
            "diagnostic": vector.metadata["diagnostic"],
            "treatment": treatment_response.message.content
        }
        res_dic["results"].append(temp)
    return res_dic

@app.route("/api/pacient", methods=["GET"])
def pacientGet():
    diagnostics = request.args.get('diagnostics').split(',')
    diagnostics = [diagnostic.strip() for diagnostic in diagnostics]
    res = {
        'content': []
    }
    for diagnostic in diagnostics:
        result = wikipedia.search(diagnostic, results = 1)[0]
        content = wikipedia.summary(result, sentences=10)
        response = chatbot.chat(
            "Resume el siguiente contenido de una manera amigable para un paciente en un parrafo y sin hablar de historia: " + content
        )
        res['content'].append({
            "diagnostic": diagnostic,
            "content": response.message.content
        })
    return res

if __name__ == "__main__":
    app.run()