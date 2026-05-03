from google import genai
from pyparsing import col
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Streamlit Chat", page_icon=":speech_balloon:")
st.title("Chatbot")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete= False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False
    

def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

def reset_interview():
    # Clear all existing session state keys
    for key in list(st.session_state.keys()):
        del st.session_state[key]


if not st.session_state.setup_complete:
    
    st.subheader('Personal information' , divider='rainbow')

    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

    st.session_state["name"] = st.text_input(label = "Name", max_chars=40, value=st.session_state["name"], placeholder="Enter your name")

    st.session_state["experience"] = st.text_area(label = "Experience",value=st.session_state["experience"], height=None,max_chars=200, placeholder="Describe your experience")

    st.session_state["skills"] = st.text_area(label= "skills", value=st.session_state["skills"], height=None, max_chars=200, placeholder="List your skills")


    st.subheader('Company and Position' , divider='rainbow')

    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if "position" not in st.session_state:
        st.session_state["position"] = "Data Scientist"
    if "company" not in st.session_state:
        st.session_state["company"] = "Amazon"
    

    col1,col2 = st.columns(2)
    with col1:
        st.radio(
            "Choose level",
            options=["Junior", "Mid-level", "Senior"],
            key="level"
        )
    with col2:
        st.selectbox(
            "Choose position",
            options=["Software Engineer", "Data Scientist", "Product Manager","Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst"],
            key="position"
        )

    st.selectbox(
            "Choose company",
            options=["Google", "Amazon", "Microsoft", "Facebook", "Apple", "Netflix", "Tesla", "IBM", "Intel", "Salesforce"],
            key="company"
    )
    
    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup complete. You can start the interview ...")

if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:

    st.info(
       """
       Start by introducing yourself.

       """,
       icon="👋"
   )

    if not st.session_state.messages:
        st.session_state.messages = [{
            "role":"system",
            "content": (
                f"You are an HR executive that interviews an interviewee called {st.session_state['name']}"
                f"with previous experience {st.session_state['experience']} and skills {st.session_state['skills']}."
                f"You should interview the candidate for a position {st.session_state['level']} {st.session_state['position']}"
                f"at the company {st.session_state['company']}"
                f"Introduce yourself with a realistic human name (not placeholders).\n"
                f"IMPORTANT RULES:\n"
                f"- You MUST refer to the role exactly as: {st.session_state['level']} {st.session_state['position']}\n"
                f"- Do NOT change the role\n"
                f"- Do NOT assume another role\n"
                f"- If you mention any role, it MUST be {st.session_state['level']} {st.session_state['position']}\n"
                f"- Do NOT use placeholders like [Your Name]\n"
                f"- Ask one interview question at a time\n"
            )
        }]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
    if st.session_state.user_message_count < 5:

        if prompt := st.chat_input("Your answer.", max_chars = 1000):
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            if st.session_state.user_message_count < 4:


                with st.chat_message("assistant"):
                    full_prompt = "\n".join(
                        [f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages]
                    )

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=full_prompt
                    )

                st.markdown(response.text)


                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.text
                })
            st.session_state.user_message_count += 1
        
        if st.session_state.user_message_count >= 5:
            st.session_state.chat_complete = True

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Feedback shown ...")

if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]
    )

    feedback_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    prompt = f"""
    You are a helpful tool that provides feedback on an interviewee performance.

    Before the feedback, give a score from 1 to 10.

    Format:
    Overall Score: <score>
    Feedback: <your feedback>

    Do NOT ask questions.

    Here is the interview:
    {conversation_history}
    """

    response = feedback_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    st.write(response.text)

    if st.button("Restart Interview", type="primary", on_click=reset_interview):
       # streamlit_js_eval(js_expressions="parent.window.location.reload()")
       pass