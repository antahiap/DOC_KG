import glob
import os
import streamlit as st
import fitz
import re
from pathlib import Path
from PIL import Image
from explanation_gpt import ExplanationGPT
from explain_paper import ExplainPaper
from file_reader import FileReader
from constants import PAPER_PDF_PATH, PAPER_REF_PATH
from app.style import css
from mycomponent import mycomponent
from app.utilities import register_callback
import app.style as style
from mycomponent import mycomponent
from netcomponent import netcomponent
from streamlit.components.v1 import html

from network_vis import VisNetwork
from network_prmpt import NetworkPrmpt
import streamlit.components.v1 as components
import time

def write_pdf(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    image_list = []
    for page_number in range(doc.page_count):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=300)  # scale up the image resolution
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        image_list.append(img)
    st.image(image_list)

def get_paper_explanation(pdf_file_name):
    file_reader = FileReader(pdf_file_name)
    file_reader.read_pdf()
    content = open(file_reader.get_text_path(), "r").read()
    explanation_gpt = ExplanationGPT(pdf_file_name.stem, context=content)
    explanation_gpt.generate_info()
    return explanation_gpt

def add_column_to_tooltip(html, column_id):
    return html.replace('<span class="tooltip">', f'<span class="tooltip" column-id="{column_id}">')

def write_explanation(index):
    explanation_idx = st.session_state.window_view[index]
    explanation_gpt = st.session_state.explanation_gpts[explanation_idx]
    if explanation_gpt:
        if not explanation_gpt.html:
            with st.spinner("Generating explanation..."):
                explanation_gpt.generate_info()
        html = explanation_gpt.html
        html = add_column_to_tooltip(html, index)
        if index > 0:
            st.subheader(explanation_gpt.topic.title())
        st.markdown(html, unsafe_allow_html=True)

def upload_file():
    file_path = st.file_uploader("Upload your paper", type=["pdf", "docx"])
    if file_path:
        with open(PAPER_PDF_PATH / file_path.name, "wb") as f:
            f.write(file_path.getbuffer())
            
        if not st.session_state.files:
            st.session_state.files = [file_path.name] #[file_stem]
        else:
            if not file_path.name in st.session_state.files:
                st.session_state.files.append(file_path.name) #file_stem)
    return file_path 

def divide_keyword_explanations(html):
    match = re.search(r'(.*?)<span class="tooltiptext">(.*?)</span>', html, re.DOTALL)
    return match.groups() if match else (None, None)

def handle_js_click():
    tooltip_info = mycomponent()
    if tooltip_info:
        print(tooltip_info)
        keyword_html, column = tooltip_info.values()
        keyword, _ = divide_keyword_explanations(keyword_html)
        print(keyword)
        if keyword:
            print(column)
            if column == '1':
                st.session_state.window_view[0] += 1
                st.session_state.window_view[1] += 1
            from_explanation_idx = st.session_state.window_view[0]
            from_explanation_gpt = st.session_state.explanation_gpts[from_explanation_idx]
            st.session_state.explanation_gpts[st.session_state.window_view[1]] = from_explanation_gpt.keywords_explanations[keyword]


def get_files_in_directory(path, ext):
    # Create the pattern to search for all PDF files in the specified path
    pdf_pattern = os.path.join(path, '**', f'*.{ext}')  # '**' will search in subdirectories too
    # Use glob to find all PDFs matching the pattern
    pdf_files = glob.glob(pdf_pattern, recursive=True)

    return pdf_files

def get_network():

    if not st.session_state.files:
        _, col1, _ = st.columns(3)
        with col1:
            st.title('Load your article to start ...')
            st.write('')
            st.write('')
            st.write('')
            st.image("static/research_data_image_g.jpg", use_container_width=True)

        nodes= None
        edges = None
        nodes2 = None
        edges2 = None
    
    else: 
        papers = st.session_state.files

        st.sidebar.title("Tools")
        th = st.sidebar.slider('Simillarity threshhold', 0.5, 1.0, .95)

        selected_paper = st.sidebar.multiselect("Loaded papers:", papers + ['All'], papers)

        ref_selected = st.sidebar.selectbox("Select a paper to load references:", ['Nothing selected'] + papers)

        if not selected_paper:

            st.session_state.nodes1 = None
            st.session_state.edges1 = None
            nodes2 = None
            edges2 = None
        
        else:
            if 'All' in selected_paper:
                selected_paper = papers

            g = VisNetwork()
            G_data = g.json_network(th, PAPER_PDF_PATH, selected_paper)
            nodes=G_data['nodes']
            edges=G_data['edges']
            st.session_state.nodes1=nodes
            st.session_state.edges1=edges
            
            if not ref_selected == 'Nothing selected':

                file_src =FileReader(PAPER_PDF_PATH / Path(ref_selected + '.pdf'))
                text_dic = file_src.read_pdf()
                ref_paper = [ref_selected] + file_src.list_reference(text_dic[-2]['references'])
                
                g_ref = VisNetwork()
                G_data = g_ref.json_network(th, PAPER_REF_PATH, ref_paper)
                
                nodes=G_data['nodes']
                edges=G_data['edges']

                st.session_state.nodes1=nodes
                st.session_state.edges1=edges

            if st.session_state.net_info:

                nodes2=st.session_state.nodes2
                edges2=st.session_state.edges2

            else:
                nodes2 = None
                edges2 = None
    
    nodes=st.session_state.nodes1
    edges=st.session_state.edges1
    
    with st.spinner('Wait for it...'):
        net_info = netcomponent(nodes=nodes, edges=edges, nodes2=nodes2, edges2=edges2 )

        if net_info:
            st.session_state.net_info = net_info

            src, dst = net_info.values()
            return
            try:
                nt_prmpt = NetworkPrmpt(G_data, selected_paper, th)
                g_prmpt = nt_prmpt.diff_paper(src, dst)
                g_zoom = VisNetwork()
                G_zoom_data = g_zoom.json_network(None, None, None, G=g_prmpt)
                st.session_state.nodes2=G_zoom_data['nodes']
                st.session_state.edges2=G_zoom_data['edges']

            except:
                return
            st.experimental_rerun()
        
        
def get_paper_explanation(pdf_file_name):
    explanation_gpt = ExplanationGPT(pdf_file_name.stem)
    explanation_gpt.fill_from_db()
    if not explanation_gpt.explanation:
        file_reader = FileReader(pdf_file_name)
        paper_json = file_reader.read_pdf()
        # paper_json = file_reader.get_json()
        explain_paper = ExplainPaper(pdf_file_name.stem, paper_json)
        explain_paper.generate_explanation()
        explanation_gpt.set_explanation(explain_paper.explanation)
    explanation_gpt.generate_info()
    return explanation_gpt

def add_column_to_tooltip(html, column_id):
    return html.replace('<span class="tooltip">', f'<span class="tooltip" column-id="{column_id}">')

def write_explanation(index):
    explanation_idx = st.session_state.window_view[index]
    explanation_gpt = st.session_state.explanation_gpts[explanation_idx]
    if explanation_gpt:
        if not explanation_gpt.html:
            with st.spinner("Generating explanation..."):
                explanation_gpt.generate_info()
        html = explanation_gpt.html
        html = add_column_to_tooltip(html, index)
        st.subheader(explanation_gpt.topic.title())
        st.markdown(html, unsafe_allow_html=True)

def divide_keyword_explanations(html):
    match = re.search(r'(.*?)<span class="tooltiptext">(.*?)</span>', html, re.DOTALL)
    return match.groups() if match else (None, None)

def handle_js_value():
    tooltip_info = st.session_state.js_click
    print(tooltip_info)
    try:
        if tooltip_info.get("html"):
            js_click(tooltip_info["html"], tooltip_info["column"])
        else:
            js_selection(tooltip_info["selection"], tooltip_info["column"])
    except Exception as e:
        print("JS error", e)
        return

def js_selection(keyword, column):
    if keyword:
        if column == 1:
            st.session_state.window_view[0] += 1
            st.session_state.window_view[1] += 1
        from_explanation_idx = st.session_state.window_view[0]
        from_explanation_gpt = st.session_state.explanation_gpts[from_explanation_idx]
        from_explanation_gpt.add_keyword_explanation(keyword)
        st.session_state.explanation_gpts[st.session_state.window_view[1]] = from_explanation_gpt.keywords_explanations[keyword]
        st.session_state.explanation_gpts[st.session_state.window_view[1] + 1] = None
        update_buttons_disabled()

def js_click(keyword_html, column):
    keyword, _ = divide_keyword_explanations(keyword_html)
    if keyword:
        if column == '1':
            st.session_state.window_view[0] += 1
            st.session_state.window_view[1] += 1
        from_explanation_idx = st.session_state.window_view[0]
        from_explanation_gpt = st.session_state.explanation_gpts[from_explanation_idx]
        st.session_state.explanation_gpts[st.session_state.window_view[1]] = from_explanation_gpt.keywords_explanations[keyword]
        st.session_state.explanation_gpts[st.session_state.window_view[1] + 1] = None
        update_buttons_disabled()

def left_button_click():
    st.session_state.window_view[0] -= 1
    st.session_state.window_view[1] -= 1
    update_buttons_disabled()

def right_button_click():
    st.session_state.window_view[0] += 1
    st.session_state.window_view[1] += 1
    update_buttons_disabled()

def update_buttons_disabled():
    st.session_state.left_button_disabled = st.session_state.window_view[0] == 0
    st.session_state.right_button_disabled = st.session_state.explanation_gpts[st.session_state.window_view[1] + 1] == None

def write_buttons():
    col1, col2 = st.columns(2)
    with col1:
        st.button("<", disabled=st.session_state.left_button_disabled, on_click=left_button_click)
    with col2:
        _, sub_col2 = st.columns([0.9, 0.1])
        sub_col2.button("\>", disabled=st.session_state.right_button_disabled, on_click=right_button_click)

def init_paper():
    with st.spinner("Generating explanation..."):
        st.session_state.window_view = [0, 1]
        st.session_state.explanation_gpts = [None] * 100
        st.session_state.explanation_gpts[0] = get_paper_explanation(PAPER_PDF_PATH / file_up.name)



st.set_page_config(
    page_title="ADPTL", 
    page_icon="static/logo.png", 
    layout="wide")
st.markdown(css, unsafe_allow_html=True)

all_files = get_files_in_directory('../data', 'docx')
print(all_files)

state_to_init = [
    ("keyword_html", None),
    ("explanation_gpts", [None] * 100),
    ("window_view", [0, 1]),
    ("left_button_disabled", True),
    ("right_button_disabled", True),
    ("selected_edge", None),
    ("net_info", None),
    ("nodes1", None),
    ("edges1", None),
    ("nodes2", None),
    ("edges2", None),
    ("files", None),
    ('tabs', "Network"),
    ('ref', None)
]
for key, value in state_to_init:
    if key not in st.session_state:
        st.session_state[key] = value

file_up = upload_file()

tab1, tab2, tab3= st.tabs(["Network", "Explanation", "Paper"])
with tab1:
    # if st.session_state.tabs == "Network":
    get_network()
    # else:
    #     st.button('Activate Network')
    

if file_up:
    # with tab2:
    #     if not st.session_state.explanation_gpts[0] or st.session_state.explanation_gpts[0].topic != Path(file_up.name).stem:
    #         st.session_state.tabs = "Explanation"
    #         init_paper()
    #     write_buttons()
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         write_explanation(0)
    #     with col2:
    #         write_explanation(1)
    #         register_callback("js_click", handle_js_value)
    #         mycomponent(key="js_click")
    with tab3:
        write_pdf(PAPER_PDF_PATH / file_up.name)




