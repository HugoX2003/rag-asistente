import streamlit as st
import requests

# --- SIDEBAR ---
with st.sidebar:
    st.title("Asistente RAG")
    st.caption("🔎 Responde sobre tus documentos")
    st.markdown(
        """
        [Ver código fuente](https://github.com/tu_repo)
        """
    )
    st.markdown("---")
    st.write("Powered by ChromaDB + LLM local + Streamlit")

# --- MAIN TITLE ---
st.markdown(
    "<h1 style='text-align: center;'>💬 Chatbot</h1>", unsafe_allow_html=True
)
st.caption(
    "<div style='text-align:center'>🚀 Un chatbot local conectado a tus documentos PDF</div>", 
    unsafe_allow_html=True
)

# --- HISTORIAL DE MENSAJES ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "¿Sobre qué documento deseas preguntar hoy?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- INPUT ---
if prompt := st.chat_input("Escribe tu pregunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Consulta a la API local
    with st.spinner("Buscando respuesta..."):
        try:
            resp = requests.get("http://localhost:8000/buscar", params={"query": prompt}, timeout=1000)
            data = resp.json()
        except Exception as e:
            msg = f"⚠️ Error al conectar con la API: {e}"
            st.session_state.messages.append({"role": "assistant", "content": msg})
            with st.chat_message("assistant"):
                st.write(msg)
            st.stop()

    respuesta = data.get("respuesta", None)
    resultados = data.get("resultados", [])

    # Formatea la respuesta
    if respuesta:
        answer = f"**Respuesta generada:**\n\n{respuesta}\n\n"
    else:
        answer = "No se generó una respuesta."

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
        if resultados:
            st.markdown("---")
            st.markdown("**Chunks relevantes:**")
            for i, chunk in enumerate(resultados[:5]):
                with st.expander(f"📄 Archivo: {chunk['archivo']} [chunk {chunk['chunk']}]"):
                    st.write(chunk["texto"])
        else:
            st.markdown("_No se encontraron chunks relevantes._")
