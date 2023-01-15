
import streamlit as st
from thermo_hygrometric.utils import plot_bar_chart_comparasion
from thermo_hygrometric import Layer, Wall
import matplotlib.pyplot as plt

#plt.style.use(["science", "retro", "no-latex"])
import pandas as pd


# -- GENERAL PAGE SETUP --
st.set_page_config(
    page_title="Thermo Hygrometric",
    page_icon="👷‍♂️",
    initial_sidebar_state="expanded",
    layout="centered",
)

# -- FUNCTIONS --
def create_layer() -> Layer:
    if "list_of_layers" not in st.session_state:
       st.session_state["list_of_layers"] = list()
    with st.form("layer_1", clear_on_submit=True):
        st.subheader("Add a new layer to the wall")
        cols = st.columns(2, gap="small")
        with cols[0]:
            name = st.text_input(label="Name", value=f"Layer n. {len(st.session_state['list_of_layers'])}")
            thickness = st.number_input(label="thickness [mm]", min_value=1., step=1., format="%.0f")/1000 # mm to m
        add_layer = st.form_submit_button(label="Add this layer to the Wall")
        if add_layer:
            st.session_state["list_of_layers"].append(
                Layer(
                    name=name,
                    thickness=thickness,
                    thermal_conductivity=0.21,
                    vapor_permeability=5.0,
                    density=1150,
                    specific_heat=1100,
                )
        )
            st.experimental_rerun() # needed to update the session state without clicking a second time and adding another layer



# -- PAGE CONTENT --
st.title("Thermo Hygrometric")


#if "list_of_walls" not in st.session_state:
#        st.session_state["list_of_walls"] = list()
#if "list_of_layers" not in st.session_state:
#       st.session_state["list_of_layers"] = list()
#
#def create_wall() -> Wall:
#    name = st.text_input(label="Wall name") 
#    new_layer = create_layer()
#    st.session_state["list_of_layers"].append(new_layer)
#
#    if st.button(label="Add Wall?"):
#        wall = Wall(name=name, layers=st.session_state["list_of_layers"])
#        st.session_state["list_of_walls"].append(wall)
#        st.session_state["list_of_layers"].clear()
#
#
st.write(st.session_state)

#waal = create_wall()
#n_layers = st.number_input(label="n_layers")
#st.write(waal)

if "list_of_walls" not in st.session_state:
    st.session_state["list_of_walls"] = list()
if "list_of_layers" not in st.session_state:
       st.session_state["list_of_layers"] = list()

with st.container():
    name = st.text_input(label="Wall name") 
    create_layer()


    wall = Wall(name=name, layers=st.session_state["list_of_layers"])
    st.write(wall)

if st.button(label="run"):
    fig = wall.plot_glaser()
    st.pyplot(fig)



# -- SIDEBAR --
with st.sidebar:
    st.subheader("Layers inserted")
    st.table(st.session_state["list_of_layers"])
    "---"

    st.subheader("Delete a layer corresponding to the selected number")
    layer_to_delete = st.selectbox(label="Layer number", options=range(len(st.session_state["list_of_layers"])))
    if st.button(label="Delete the selected layer"):
        st.session_state["list_of_layers"].pop(layer_to_delete)
        st.experimental_rerun() # needed to update the session state so the table above is refreshed

    "---"
    if st.button(label="Delete all layers"):
        st.session_state["list_of_layers"].clear()
    if st.button(label="Delete everything saved"):
        st.session_state.clear()

