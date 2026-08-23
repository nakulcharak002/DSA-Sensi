"""
Custom CSS for the DSA Sensei Streamlit UI.
"""


def get_custom_css() -> str:
    return """
<style>

.block-container{
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.stButton > button {
    width: 100%;
    height: 46px;
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid rgba(139, 92, 246, 0.35);
    background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%);
    color: #FAFAFA;
    transition: all 0.15s ease-in-out;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(139, 92, 246, 0.35);
    border-color: #A78BFA;
}

.stButton > button:active {
    transform: translateY(0px);
}

textarea, .stTextInput > div > div > input {
    border-radius: 10px !important;
}

[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    background: #1E1E2F;
    border: 1px solid rgba(139, 92, 246, 0.15);
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: rgba(139, 92, 246, 0.12);
    border: 1px solid rgba(139, 92, 246, 0.3);
}

section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(139, 92, 246, 0.15);
}

h1 {
    background: linear-gradient(90deg, #A78BFA, #8B5CF6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

.stCodeBlock, pre {
    border-radius: 10px !important;
    border: 1px solid rgba(139, 92, 246, 0.2);
}

[data-testid="stMetric"] {
    background: #1E1E2F;
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 12px;
    padding: 0.75rem;
}

.streamlit-expanderHeader {
    border-radius: 8px;
}

::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: rgba(139, 92, 246, 0.4);
    border-radius: 4px;
}

</style>
"""
