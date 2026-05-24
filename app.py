import streamlit as st
import google.generativeai as genai

LUPA_PROMPT = """Você é o MomaLupa. Identifique caracteres ambíguos (l, I, 0, O, 1) na entrada.
Responda APENAS em JSON, seguindo esta estrutura:
{
  "analise": [{"caractere": "...", "significado": "...", "dica": "..."}],
  "mensagem_final": "A anotação em papel é a forma mais segura de guardar sua chave."
}"""

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=LUPA_PROMPT)
except Exception as e:
    st.error("Erro ao carregar a API")
    st.code(str(e))
    st.stop()

st.set_page_config(page_title="MomaLupa", page_icon="🔍")
st.image("logo.PNG", width=300)
st.title("🔍 MomaLupa")
st.markdown("*Identificador de Caracteres Ambíguos*")

entrada = st.text_input("Cole o código aqui para decifrar:")

if st.button("Decifrar"):
    if entrada:
        with st.spinner("🔍 Analisando caracteres..."):
            try:
                response = model.generate_content(entrada)
                st.json(response.text)
            except Exception as e:
                st.warning("🔍 A Lupa precisa descansar um momento. Tente novamente em breve.")
    else:
        st.warning("Por favor, cole um código para decifrar.")

if st.button("Limpar Tudo/Destruir Sessão"):
    st.rerun()




