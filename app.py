import streamlit as st
import requests

# 🔗 Your n8n webhook URL (PRODUCTION)
# Example:
N8N_WEBHOOK_URL = "https://sudha-mad-max-1997.app.n8n.cloud/webhook/8cf103a1-e3bb-4c4d-9f95-19a3ad2e61a0"



def call_n8n_generate_code(prompt: str, mode: str) -> str:
    """
    Send the user's prompt + mode to n8n and get back generated Python code.
    mode: "app" or "game"
    Returns the code as a string, or "" on failure.
    """
    try:
        payload = {
            "prompt": prompt,
            "mode": mode,
        }
        resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        code = (data.get("code") or "").strip()
        return code
    except Exception as e:
        st.error(f"Error contacting n8n: {e}")
        return ""


def main():
    st.set_page_config(
        page_title="AI Web App/Game Generator",
        layout="wide",
    )

    st.title("🧠 AI-Powered Web App/Game Generator")
    st.write(
        "Describe the app or game you want. "
        "On click of **Generate & Run**, your idea is sent to an n8n workflow, "
        "an LLM generates Streamlit code, and the app/game opens below."
    )

    # Sidebar instructions
    with st.sidebar:
        st.header("How it works")
        st.markdown(
            """
            1. Enter an idea for an app or game  
            2. Choose **App** or **Game**  
            3. Click **Generate & Run**  
            4. Use or play the generated app directly on this page  
            """
        )
        st.markdown("---")
        st.markdown("**Backend:** n8n + LLM\n**Frontend:** Streamlit")

    # Prompt input
    prompt = st.text_area(
        "Describe the app or game you want to generate:",
        height=150,
        placeholder=(
            "Examples:\n"
            "- A simple calculator with history\n"
            "- A to-do list app with add/delete/complete\n"
            "- A number guessing game\n"
            "- A small snake game with arrow buttons\n"
        ),
    )

    mode_label = st.radio(
        "Select what you want to generate:",
        options=["App", "Game"],
        index=1,  # default to Game if you like
        horizontal=True,
    )
    mode_value = "app" if mode_label == "App" else "game"

    # Keep latest code in session (for debugging or re-run if needed)
    if "generated_code" not in st.session_state:
        st.session_state["generated_code"] = ""

    # Main action button: Generate + Run
    if st.button("🎮 Generate & Run", type="primary"):
        if not prompt.strip():
            st.warning("Please enter a description for your app or game first.")
        else:
            with st.spinner("Generating code via n8n + LLM and running app..."):
                code = call_n8n_generate_code(prompt.strip(), mode_value)
                if not code:
                    st.error(
                        "No code received from n8n. "
                        "Check your n8n workflow, AI Agent output, or logs."
                    )
                else:
                    st.session_state["generated_code"] = code

                    # Prepare shared namespace and inject Streamlit
                    local_ns = {"st": st}
                    try:
                        # Execute generated code; imports and functions land in local_ns
                        exec(code, local_ns, local_ns)

                        render_func = local_ns.get("render_app")
                        if callable(render_func):
                            st.info("Running generated app below 👇")
                            render_func()
                        else:
                            st.error(
                                "render_app() function not found in generated code.\n"
                                "Ensure your n8n AI Agent always defines:\n"
                                "    def render_app():\n"
                            )
                    except Exception as e:
                        st.error(f"Error while running the generated app: {e}")
    else:
        # If user already generated something in this session, allow re-render on refresh
        if st.session_state.get("generated_code"):
            local_ns = {"st": st}
            try:
                exec(st.session_state["generated_code"], local_ns, local_ns)
                render_func = local_ns.get("render_app")
                if callable(render_func):
                    st.info("Last generated app is shown below 👇")
                    render_func()
            except Exception:
                # Silent failure here; main path is the button above
                pass


if __name__ == "__main__":
    main()
