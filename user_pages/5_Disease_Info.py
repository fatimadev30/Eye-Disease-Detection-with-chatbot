import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import render_medical_disclaimer, require_login

require_login()

st.title("ℹ️ Disease Information")
render_medical_disclaimer()

st.markdown("""
### Choroidal Neovascularization (CNV)
Choroidal Neovascularization involves the growth of new blood vessels that originate from the choroid through a break in the Bruch membrane into the sub–retinal pigment epithelium (sub-RPE) or subretinal space. This is a major cause of visual loss.

### Diabetic Macular Edema (DME)
Diabetic Macular Edema is an accumulation of fluid in the macula part of the retina that controls our most detailed vision abilities—due to leaking blood vessels. In order to develop DME, you must first have diabetic retinopathy. DME is the most common cause of vision loss among people with diabetic retinopathy.

### Drusen
Drusen are yellow deposits under the retina. Drusen are made up of lipids, a fatty protein. Drusen likely do not cause age-related macular degeneration (AMD). But having drusen increases a person's risk of developing AMD.

### Normal Retina
A normal retina is characterized by a healthy, organized structure of its cellular layers. The macula, which is responsible for central vision, is free of fluid, swelling, or yellow deposits (drusen). The retinal pigment epithelium (RPE) appears intact and uninterrupted.
""")
