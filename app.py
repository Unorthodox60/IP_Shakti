import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Ayurveda IPR Assistant", layout="wide")

st.title("Ayurveda IPR Assistant 🌿")
st.caption("Disclaimer: This is information, not legal advice.")

# Jurisdiction Toggle
jurisdiction = st.sidebar.radio("Select Jurisdiction", ["India", "International"])
st.sidebar.markdown(f"**Active Jurisdiction Badge:** 🏷️ **{jurisdiction}**")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "classifier_node" not in st.session_state:
    st.session_state.classifier_node = "q1"
    st.session_state.classification_done = False

# Sidebar: Classification Flow
st.sidebar.header("Formulation Classification")
if not st.session_state.classification_done:
    try:
        response = requests.post(f"{API_URL}/classify", json={"node_id": st.session_state.classifier_node})
        if response.status_code == 200:
            node_data = response.json()
            if node_data.get("type") == "classification":
                st.sidebar.success(f"**Classification:** {node_data['category']}")
                st.sidebar.markdown(node_data['explanation'])
                st.session_state.classification_done = True
                if st.sidebar.button("Reset Classification"):
                    st.session_state.classifier_node = "q1"
                    st.session_state.classification_done = False
                    st.rerun()
            else:
                st.sidebar.markdown(f"**{node_data['text']}**")
                for option in node_data['options']:
                    if st.sidebar.button(option['label']):
                        st.session_state.classifier_node = option['next']
                        st.rerun()
    except Exception as e:
        st.sidebar.error("Backend not running. Start api.py first.")
else:
    # Just show the final result again
    try:
        response = requests.post(f"{API_URL}/classify", json={"node_id": st.session_state.classifier_node})
        if response.status_code == 200:
            node_data = response.json()
            st.sidebar.success(f"**Classification:** {node_data['category']}")
            st.sidebar.markdown(node_data['explanation'])
            if st.sidebar.button("Reset Classification"):
                st.session_state.classifier_node = "q1"
                st.session_state.classification_done = False
                st.rerun()
    except:
        pass


# Main Chat Interface
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "confidence" in msg:
            color = "green" if msg["confidence"] == "High" else "orange" if msg["confidence"] == "Medium" else "red"
            st.markdown(f"**Confidence:** <span style='color:{color}'>{msg['confidence']}</span>", unsafe_allow_html=True)
            if msg["confidence"] == "Low":
                st.warning("⚠️ Confidence is Low. [Escalate to human IP facilitator](#)")
        
        if "citations" in msg and msg["citations"]:
            with st.expander("Sources & Citations"):
                for cit in msg["citations"]:
                    st.write(f"- {cit}")

if prompt := st.chat_input("Ask a question about Ayurveda IP..."):
    # Append user message
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(f"{API_URL}/chat", json={"query": prompt, "jurisdiction": jurisdiction})
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "")
                    confidence = data.get("confidence", "Low")
                    citations = data.get("citations", [])
                    
                    st.write(answer)
                    
                    color = "green" if confidence == "High" else "orange" if confidence == "Medium" else "red"
                    st.markdown(f"**Confidence:** <span style='color:{color}'>{confidence}</span>", unsafe_allow_html=True)
                    if confidence == "Low":
                        st.warning("⚠️ Confidence is Low. [Escalate to human IP facilitator](#)")
                        
                    if citations:
                        with st.expander("Sources & Citations"):
                            for cit in citations:
                                st.write(f"- {cit}")
                                
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "confidence": confidence,
                        "citations": citations
                    })
                else:
                    st.error("Error from backend.")
            except Exception as e:
                st.error("Cannot connect to API backend.")
