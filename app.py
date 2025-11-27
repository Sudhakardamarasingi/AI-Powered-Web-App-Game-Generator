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
            "mode": mode,  # "app" or "game"
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
        "This app lets you generate simple applications or games using natural language.\n\n"
        "**Generate App** → sends your idea to n8n + LLM and returns Python Streamlit code.\n"
        "**Run App** → executes the generated code inside this page so you can use or play it."
    )

    # Sidebar info
    with st.sidebar:
        st.header("How it works")
        st.markdown(
            """
            1. Enter an idea for an app or game  
            2. Choose **App** or **Game** mode  
            3. Click **Generate App** (calls n8n + LLM)  
            4. Click **Run App** to execute the generated code  
            """
        )
        st.markdown("---")
        st.markdown("**Backend:** n8n + LLM\n**Frontend:** Streamlit")

    # Main input
    prompt = st.text_area(
        "Describe the app or game you want to generate:",
        height=150,
        placeholder=(
            "Examples:\n"
            "- A simple calculator with history\n"
            "- A to-do list app with add/delete/complete\n"
            "- A number guessing game\n"
            "- A small snake game with buttons\n"
        ),
    )

    mode_label = st.radio(
        "Select what you want to generate:",
        options=["App", "Game"],
        index=0,
        horizontal=True,
    )
    mode_value = "app" if mode_label == "App" else "game"

    col_left, col_right = st.columns(2)

    # Store generated code in session
    if "generated_code" not in st.session_state:
        st.session_state["generated_code"] = ""

    # --------- Generate App (core action 1) ----------
    with col_left:
        if st.button("🚀 Generate App", type="primary"):
            if not prompt.strip():
                st.warning("Please enter a description for your app or game first.")
            else:
                with st.spinner("Generating code via n8n + LLM..."):
                    code = call_n8n_generate_code(prompt.strip(), mode_value)
                    if not code:
                        st.error(
                            "No code received from n8n. "
                            "Check your n8n workflow, AI Agent output, or logs."
                        )
                    else:
                        st.session_state["generated_code"] = code
                        st.success("✅ Code generated successfully!")

    # --------- Run App (core action 2) ----------
    with col_right:
        if st.button("▶ Run App"):
            code = st.session_state.get("generated_code", "").strip()
            if not code:
                st.warning("Generate the app code first before running.")
            else:
                st.info("Running generated app below...")

                # Single namespace for exec; pre-inject Streamlit
                # so 'st' is always defined inside generated code.
                local_ns = {"st": st}

                try:
                    # Execute generated code; imports and functions land in local_ns
                    exec(code, local_ns, local_ns)

                    render_func = local_ns.get("render_app")
                    if callable(render_func):
                        render_func()
                    else:
                            st.error(
                                "render_app() function not found in generated code.\n"
                                "Ensure your n8n AI Agent always defines:\n"
                                "    def render_app():\n"
                            )
                except Exception as e:
                    st.error(f"Error while running the generated app: {e}")

    st.markdown("---")
    st.subheader("Generated Code (for reference)")

    generated_code = st.session_state.get("generated_code", "").strip()
    if generated_code:
        st.code(generated_code, language="python")
    else:
        st.write("No code generated yet. Enter a prompt and click **Generate App**.")


if __name__ == "__main__":
    main()
