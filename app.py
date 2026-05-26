import streamlit as st
import google.generativeai as genai
from pydantic import BaseModel
from typing import List
import re

# ==================== MODELO PYDANTIC ====================
class CaractereAnalise(BaseModel):
    caractere: str
    significado: str
    dica: str

class LupaResponse(BaseModel):
    analise: List[CaractereAnalise]
    mensagem_final: str

# ==================== PROMPT ====================
LUPA_PROMPT = """
Você é o M.O.M.A. Lupa. Sua função é identificar caracteres ambíguos (l/I/1, 0/O, etc.) em códigos, chaves ou seed phrases.

Responda **APENAS** com JSON válido, seguindo exatamente esta estrutura:
{
  "analise": [
    {"caractere": "l", "significado": "pode ser confundido com I ou 1", "dica": "escreva sempre como 'l' minúsculo ou use fonte monospace"},
    ...
  ],
  "mensagem_final": "A anotação em papel é a forma mais segura de guardar sua chave."
}
"""

# ==================== VALIDAÇÃO ====================
def validar_json(texto: str) -> LupaResponse:
    match = re.search(r'\{[\s\S]*\}', texto)
    if not match:
        raise ValueError("JSON não encontrado")
    json_str = match.group(0)
    return LupaResponse.model_validate_json(json_str)

# ==================== INTERFACE BONITA ====================
st.set_page_config(page_title="M.O.M.A. Lupa", page_icon="🔍", layout="centered")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.5-flash", system_instruction=LUPA_PROMPT)
except Exception:
    st.error("🔍 A Lupa não conseguiu despertar... Tente novamente mais tarde.")
    st.stop()

st.image("logo.PNG", width=300)
st.title("🔍 M.O.M.A. Lupa")
st.markdown("*Identificador de Caracteres Ambíguos*")
st.caption("Proteja sua chave contra confusões visuais")

entrada = st.text_area(
    "Cole o código ou seed phrase aqui:",
    height=150,
    placeholder="Ex: 1lI0O l0l0 1I1I ..."
)

if st.button("🔍 Decifrar", type="primary"):
    if entrada.strip():
        with st.spinner("🔍 Analisando caracteres ambíguos..."):
            try:
                response = model.generate_content(entrada)
                resultado = validar_json(response.text)

                st.success("✅ Análise concluída!")

                for item in resultado.analise:
                    st.markdown(f"**{item.caractere}** → {item.significado}")
                    st.caption(f"Dica: {item.dica}")
                    st.divider()

                st.markdown(f"**{resultado.mensagem_final}**")

            except Exception:
                st.warning("🔍 A Lupa precisa descansar um momento. Tente novamente em breve.")
    else:
        st.warning("Por favor, cole um código para analisar.")

if st.button("🔄 Limpar Tudo"):
    st.rerun()
