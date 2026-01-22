import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle
import io

# Page configuration
st.set_page_config(
    page_title="PMEG Template Generator",
    page_icon="🏥",
    layout="wide"
)

# Vessel name options
VESSEL_OPTIONS = [
    "Celiac Trunk",
    "SMA",
    "LRA",
    "RRA",
    "IMA",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5"
]

# Short names for display on template
VESSEL_SHORT_NAMES = {
    "Celiac Trunk": "CT",
    "SMA": "SMA",
    "LRA": "LRA",
    "RRA": "RRA",
    "IMA": "IMA",
    "F1": "F1",
    "F2": "F2",
    "F3": "F3",
    "F4": "F4",
    "F5": "F5"
}

# Function to convert clock position to degrees for 2D template
# Template layout: 9 o'clock on LEFT, 12 in CENTER, 3 o'clock on RIGHT
def clock_to_template_position(clock_position, circumference):
    # We want: 9=left edge (0), 12=center (circumference/2), 3=right edge (circumference)
    # Clock positions: 9, 10, 11, 12, 1, 2, 3 map to 0 -> circumference
    # And 3, 4, 5, 6, 7, 8, 9 wrap around
    
    # Map clock to position where 9=0, 12=0.5, 3=1.0 (as fraction of circumference)
    if clock_position >= 9:
        # 9=0, 10=1/12, 11=2/12, 12=3/12
        fraction = (clock_position - 9) / 12
    else:
        # 1=4/12, 2=5/12, 3=6/12, 4=7/12, 5=8/12, 6=9/12, 7=10/12, 8=11/12
        fraction = (clock_position + 3) / 12
    
    return fraction * circumference

# Function to get available vessel options (exclude already used ones)
def get_available_vessels():
    used_vessels = [fen['vessel'] for fen in st.session_state.fenestrations]
    available = []
    for vessel in VESSEL_OPTIONS:
        if vessel.startswith("F") or vessel not in used_vessels:
            available.append(vessel)
    return available

# Initialize session state
if 'fenestrations' not in st.session_state:
    st.session_state.fenestrations = []

# Title and description
st.title("🏥 PMEG Template Generator")
st.markdown("**Proof of Concept for Physician-Modified Endograft Template Generation**")
st.markdown("Design fenestrations on vascular grafts and generate printable templates")

# Sidebar controls
st.sidebar.header("Graft Configuration")
graft_diameter = st.sidebar.selectbox(
    "Graft Diameter (mm)", 
    [20, 24, 28, 32, 36], 
    index=2
)
graft_length = st.sidebar.slider("Graft Length (mm)", 80, 200, 120)
fenestration_size = st.sidebar.slider("Fenestration Size (mm)", 4, 12, 6)

st.sidebar.header("Fenestration Controls")
if st.sidebar.button("Clear All Fenestrations", type="secondary"):
    st.session_state.fenestrations = []
    st.rerun()

# Main layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("3D Graft View")
    st.markdown("*Add fenestrations using clock positions (12 o'clock = anterior)*")
    
    # Create 3D-like visualization
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    ax1.set_xlim(-120, 120)
    ax1.set_ylim(-150, 150)
    ax1.set_aspect('equal')
    
    # TOP of graft at y = 100 (top of image)
    # BOTTOM of graft at y = -100 (bottom of image)
    
    # Top ellipse (proximal end)
    ellipse_top = patches.Ellipse((0, 100), 160, 60, linewidth=2, 
                                 edgecolor='black', facecolor='lightblue', alpha=0.3)
    ax1.add_patch(ellipse_top)
    
    # Bottom ellipse (distal end)
    ellipse_bottom = patches.Ellipse((0, -100), 160, 60, linewidth=2, 
                                   edgecolor='black', facecolor='lightblue', alpha=0.3)
    ax1.add_patch(ellipse_bottom)
    
    # Side lines
    ax1.plot([-80, -80], [-100, 100], 'k-', linewidth=2)
    ax1.plot([80, 80], [-100, 100], 'k-', linewidth=2)
    
    # Clock position labels
    ax1.text(0, 135, "12", fontsize=9, ha='center', va='center', color='blue')
    ax1.text(0, 65, "6", fontsize=9, ha='center', va='center', color='blue')
    ax1.text(-95, 100, "9", fontsize=9, ha='center', va='center', color='blue')
    ax1.text(95, 100, "3", fontsize=9, ha='center', va='center', color='blue')
    
    # Draw fenestrations on 3D view
    for i, fen in enumerate(st.session_state.fenestrations):
        clock = fen['clock']
        # Map clock to x position: 9=-80, 12=0, 3=80
        if clock >= 9:
            x = -80 + ((clock - 9) / 3) * 80  # 9->-80, 12->0
        elif clock <= 3:
            x = (clock / 3) * 80  # 0->0, 3->80
        else:
            x = 80 - ((clock - 3) / 6) * 160  # 3->80, 6->0, 9->-80
        
        # position from top: 0 -> y=100, graft_length -> y=-100
        y = 100 - (fen['position'] / graft_length) * 200
        
        circle = Circle((x, y), 8, color='red', alpha=0.7)
        ax1.add_patch(circle)
        short_name = VESSEL_SHORT_NAMES.get(fen['vessel'], fen['vessel'])
        ax1.text(x + 12, y, short_name, fontsize=10, fontweight='bold')
    
    # Labels
    ax1.text(0, 145, "TOP (Proximal)", fontsize=10, ha='center', color='green', fontweight='bold')
    ax1.text(0, -140, "BOTTOM (Distal)", fontsize=10, ha='center', color='green', fontweight='bold')
    
    ax1.set_title(f"Graft: {graft_diameter}mm x {graft_length}mm")
    ax1.axis('off')
    
    st.pyplot(fig1)
    plt.close(fig1)
    
    # Fenestration input
    st.markdown("**Add Fenestration:**")
    
    available_vessels = get_available_vessels()
    new_vessel = st.selectbox(
        "Vessel / Fenestration Name",
        available_vessels,
        index=0,
        help="Select the target vessel or use F1, F2, etc. for custom fenestrations"
    )
    
    col1a, col1b = st.columns(2)
    with col1a:
        new_position = st.number_input("Position from top (mm)", 0, graft_length, 60)
    with col1b:
        new_clock = st.selectbox(
            "Clock Position",
            [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            index=0,
            help="12 o'clock = anterior (front), 6 o'clock = posterior (back)"
        )
    
    if st.button("Add Fenestration"):
        st.session_state.fenestrations.append({
            'vessel': new_vessel,
            'position': new_position,
            'clock': new_clock
        })
        st.rerun()

with col2:
    st.subheader("2D Template (Unwrapped)")
    st.markdown("*Printable template - 9 o'clock at left, 12 at center, 3 at right*")
    
    # Calculate dimensions
    circumference = np.pi * graft_diameter
    
    # Create 2D template
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    
    # Draw template rectangle
    rect = Rectangle((0, 0), circumference, graft_length, 
                    linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax2.add_patch(rect)
    
    # Draw clock position markers: 9 at left, 12 at center, 3 at right, 6 at edges
    clock_markers = [
        (9, 0),                      # 9 o'clock at left edge
        (12, circumference / 2),     # 12 o'clock at center
        (3, circumference),          # 3 o'clock at right edge
        (6, circumference / 4),      # 6 o'clock between 9 and 12
    ]
    
    # Add second 6 o'clock marker on the other side
    ax2.axvline(x=0, color='blue', linestyle='--', linewidth=1, alpha=0.5)
    ax2.text(0, graft_length + 5, "9", fontsize=10, ha='center', color='blue', fontweight='bold')
    
    ax2.axvline(x=circumference/4, color='blue', linestyle='--', linewidth=1, alpha=0.3)
    ax2.text(circumference/4, graft_length + 5, "6", fontsize=9, ha='center', color='blue')
    
    ax2.axvline(x=circumference/2, color='blue', linestyle='--', linewidth=1, alpha=0.5)
    ax2.text(circumference/2, graft_length + 5, "12", fontsize=10, ha='center', color='blue', fontweight='bold')
    
    ax2.axvline(x=3*circumference/4, color='blue', linestyle='--', linewidth=1, alpha=0.3)
    ax2.text(3*circumference/4, graft_length + 5, "6", fontsize=9, ha='center', color='blue')
    
    ax2.axvline(x=circumference, color='blue', linestyle='--', linewidth=1, alpha=0.5)
    ax2.text(circumference, graft_length + 5, "3", fontsize=10, ha='center', color='blue', fontweight='bold')
    
    # Draw fenestrations
    for i, fen in enumerate(st.session_state.fenestrations):
        x = clock_to_template_position(fen['clock'], circumference)
        y = graft_length - fen['position']
        
        circle = Circle((x, y), fenestration_size/2, color='red', alpha=0.7)
        ax2.add_patch(circle)
        short_name = VESSEL_SHORT_NAMES.get(fen['vessel'], fen['vessel'])
        ax2.text(x + fenestration_size/2 + 2, y, short_name, fontsize=10, fontweight='bold')
    
    ax2.set_aspect('equal')
    ax2.set_xlim(-5, circumference + 15)
    ax2.set_ylim(-5, graft_length + 15)
    ax2.set_xlabel('Circumference (mm)')
    ax2.set_ylabel('Distance from Bottom (mm)')
    ax2.set_title('Printable Template')
    ax2.grid(True, alpha=0.3)
    
    st.pyplot(fig2)
    plt.close(fig2)

# Fenestration list
if st.session_state.fenestrations:
    st.subheader("Fenestrations List")
    sorted_fens = sorted(enumerate(st.session_state.fenestrations), key=lambda x: x[1]['position'])
    for orig_idx, fen in sorted_fens:
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.write(f"**{fen['vessel']}:** Position: {fen['position']:.1f}mm from top, Clock: {fen['clock']} o'clock, Size: {fenestration_size}mm")
        with col_b:
            if st.button(f"Delete", key=f"del_{orig_idx}"):
                st.session_state.fenestrations.pop(orig_idx)
                st.rerun()

# Vessel reference
st.subheader("🩺 Vessel Reference")
col_ref1, col_ref2 = st.columns(2)
with col_ref1:
    st.markdown("""
    | Abbreviation | Full Name |
    |--------------|-----------|
    | CT | Celiac Trunk |
    | SMA | Superior Mesenteric Artery |
    | LRA | Left Renal Artery |
    """)
with col_ref2:
    st.markdown("""
    | Abbreviation | Full Name |
    |--------------|-----------|
    | RRA | Right Renal Artery |
    | IMA | Inferior Mesenteric Artery |
    | F1-F5 | Custom Fenestrations |
    """)

# Clock position reference
st.subheader("🕐 Clock Position Reference")
col_clk1, col_clk2 = st.columns(2)
with col_clk1:
    st.markdown("""
    | Clock | Position |
    |-------|----------|
    | 12 | Anterior (front) |
    | 3 | Left |
    | 6 | Posterior (back) |
    | 9 | Right |
    """)
with col_clk2:
    st.markdown("""
    | Clock | Position |
    |-------|----------|
    | 1-2 | Anterior-Left |
    | 4-5 | Posterior-Left |
    | 7-8 | Posterior-Right |
    | 10-11 | Anterior-Right |
    """)

# Print instructions
st.subheader("📄 Print Instructions")
st.info("""
1. Ensure printer is set to "Actual Size" or "100%" scale
2. Use standard A4/Letter paper
3. Sterilize printed template before use
4. Align 12 o'clock mark with anterior position on graft
5. Wrap template around actual graft (9 o'clock = right side of patient)
6. Use holes as cutting guides
""")

# Download template
if st.session_state.fenestrations:
    fig_download, ax_download = plt.subplots(figsize=(12, 10))
    
    circumference = np.pi * graft_diameter
    rect = Rectangle((0, 0), circumference, graft_length, 
                    linewidth=2, edgecolor='black', facecolor='white')
    ax_download.add_patch(rect)
    
    # Clock markers
    ax_download.axvline(x=0, color='blue', linestyle='--', linewidth=1, alpha=0.5)
    ax_download.text(0, graft_length + 5, "9 o'clock", fontsize=9, ha='center', color='blue')
    
    ax_download.axvline(x=circumference/2, color='blue', linestyle='--', linewidth=1, alpha=0.5)
    ax_download.text(circumference/2, graft_length + 5, "12 o'clock", fontsize=9, ha='center', color='blue')
    
    ax_download.axvline(x=circumference, color='blue', linestyle='--', linewidth=1, alpha=0.5)
    ax_download.text(circumference, graft_length + 5, "3 o'clock", fontsize=9, ha='center', color='blue')
    
    for i, fen in enumerate(st.session_state.fenestrations):
        x = clock_to_template_position(fen['clock'], circumference)
        y = graft_length - fen['position']
        circle = Circle((x, y), fenestration_size/2, color='red', alpha=0.7)
        ax_download.add_patch(circle)
        short_name = VESSEL_SHORT_NAMES.get(fen['vessel'], fen['vessel'])
        ax_download.text(x + fenestration_size/2 + 2, y, short_name, fontsize=10, fontweight='bold')
    
    ax_download.set_aspect('equal')
    ax_download.set_xlim(-5, circumference + 15)
    ax_download.set_ylim(-5, graft_length + 15)
    ax_download.set_xlabel('Circumference (mm)')
    ax_download.set_ylabel('Distance from Bottom (mm)')
    ax_download.set_title(f'Graft Template - {graft_diameter}mm x {graft_length}mm')
    ax_download.grid(True, alpha=0.3)
    
    buf = io.BytesIO()
    fig_download.savefig(buf, format='pdf', bbox_inches='tight', dpi=300)
    buf.seek(0)
    plt.close(fig_download)
    
    st.download_button(
        label="📥 Download Template (PDF)",
        data=buf.getvalue(),
        file_name=f"graft_template_{graft_diameter}mm_{graft_length}mm.pdf",
        mime="application/pdf"
    )

# Footer
st.markdown("---")
st.markdown("**⚠️ Disclaimer:** This is a prototype for demonstration purposes only. Not intended for clinical use without proper validation and regulatory approval.")
