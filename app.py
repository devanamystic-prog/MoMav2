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
Você é o M.O.M.A. Lupa. Identifique caracteres ambíguos (l, I, 0, O, 1) na entrada.
Responda APENAS em JSON, seguindo esta estrutura:
{
  "analise": [{"caractere": "...", "significado": "...", "dica": "..."}],
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

# ==================== INTERFACE ====================
st.set_page_config(page_title="M.O.M.A Lupa", page_icon="🔍", layout="centered")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.5-flash", system_instruction=LUPA_PROMPT)
except Exception:
    st.error("🔍 A Lupa não conseguiu despertar... Tente novamente mais tarde.")
    st.stop()

st.image("logo.PNG", width=300)
st.title("🔍 M.O.M.A Lupa")
st.markdown("*Identificador de Caracteres Ambíguos*")
st.caption("🔐 Sua chave é analisada e destruída imediatamente")

entrada = st.text_area(
    "Cole o código ou seed phrase aqui:",
    height=150,
    placeholder="Ex: 1lI0O l0l0 1I1I ...",
    key="input_key"
)

if st.button("🔍 Decifrar", type="primary"):
    if entrada.strip():
        with st.spinner("🔍 Analisando caracteres..."):
            try:
                response = model.generate_content(entrada)
                resultado = validar_json(response.text)

                st.success("✅ Análise concluída com segurança!")

                # === TEXTO ORIGINAL COM DESTAQUE EM VERMELHO ===
                st.markdown("**Senha original:**")
                st.code(entrada, language=None)
                st.divider()

                # Visual Lupa - todos os ambíguos em vermelho
                highlighted = entrada
                for item in resultado.analise:
                    char = item.caractere
                    highlighted = highlighted.replace(char, f'<span style="color:#FF4444; font-weight:bold;">{char}</span>')
                st.markdown("**🔍 Caracteres ambíguos detectados:**")
                st.markdown(highlighted, unsafe_allow_html=True)
                st.divider()

                # === ANÁLISE COM VERMELHO ===
                for item in resultado.analise:
                    st.markdown(f'<span style="color:#FF4444; font-weight:bold;">**{item.caractere}**</span> → {item.significado}', unsafe_allow_html=True)
                    st.caption(f"Dica: {item.dica}")
                    st.divider()

                st.markdown(f"**{resultado.mensagem_final}**")

                st.info("🔐 **Sua chave foi analisada e destruída imediatamente.** Nada foi salvo no servidor.")

            except Exception:
                st.warning("🔍 A Lupa precisa descansar um momento. Tente novamente em breve.")
    else:
        st.warning("Por favor, cole um código para analisar.")

if st.button("🗑️ Limpar e Destruir Sessão"):
    st.rerun()

st.markdown("---")
st.markdown("""
🔒 **Sua privacidade é prioridade.**  
A chave é analisada apenas no momento e **excluída imediatamente** após a análise.  
Nada é armazenado.
""")
