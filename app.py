import streamlit as st
from openai import OpenAI
import yaml
import streamlit_authenticator as stauth


def home():
    with st.sidebar:
        openai_api_key = st.text_input(
            "OpenAI API Key", key="chatbot_api_key", type="password"
        )
        "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
        "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
        "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

    st.title("💬 Chatbot")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "system",
                "content": "あなたはマーケティングの専門家として、ユーザーの課題解決してください。",
            },
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        client = OpenAI(api_key=openai_api_key)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=st.session_state.messages
        )
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)


pages = {
    "メイン": [
        st.Page(
            home,
            title="Home",
            icon="🏠",
        ),
        st.Page(
            "pages/sample.py",
            title="サンプル",
            icon="🗒",
        ),
    ]
}


def not_logged_in():
    def empty_page():
        pass

    pg = st.navigation([st.Page(empty_page)])
    pg.run()
    st.stop()


with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.loader.SafeLoader)

authenticator = stauth.Authenticate(
    credentials=config["credentials"],
    cookie_name=config["cookie"]["name"],
    cookie_key=config["cookie"]["key"],
)
authenticator.login()


if st.session_state["authentication_status"]:
    page = st.navigation(pages)
    page.run()
    # home()
    with st.sidebar:
        st.divider()
        authenticator.logout("Logout", "sidebar")
elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
    not_logged_in()
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
    not_logged_in()
