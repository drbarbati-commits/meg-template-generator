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

# Function to convert clock position to X position on 2D template
# Template: 9 o'clock = LEFT (0), 12 o'clock = CENTER (0.5), 3 o'clock = RIGHT (1.0)
def clock_to_x_fraction(clock_position):
    # Clock face unwrapped: 9 -> 10 -> 11 -> 12 -> 1 -> 2 -> 3
    # Maps to X fraction:   0 -> 1/6 -> 2/6 -> 3/6 -> 4/6 -> 5/6 -> 6/6
    
    if clock_position == 9:
        return 0.0
    elif clock_position == 10:
        return 1/6
    elif clock_position == 11:
        return 2/6
    elif clock_position == 12:
        return 3/6  # Center = 0.5
    elif clock_position == 1:
        return 4/6
    elif clock_position == 2:
        return 5/6
    elif clock_position == 3:
        return 6/6  # Right edge = 1.0
    elif clock_position == 4:
        return 7/6  # Beyond 3, wraps but we show it
    elif clock_position == 5:
        return 8/6
    elif clock_position == 6:
        return 9/6  # This would be at 1.5 (off the main template)
    elif clock_position == 7:
        return -2/6  # Before 9
    elif clock_position == 8:
        return -1/6
    
    return 0.5  # Default to center

# Function to get available vessel options
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
        if clock == 12:
            x = 0
        elif clock == 9:
            x = -80
        elif clock == 3:
            x = 80
        elif clock == 6:
            x = 0  # Back/front center
        elif clock in [10, 11]:
            x = -80 + (clock - 9) * (80 / 3)  # 10->-53, 11->-27
        elif clock in [1, 2]:
            x = clock * (80 / 3)  # 1->27, 2->53
        elif clock in [4, 5]:
            x = 80 - (clock - 3) * (80 / 3)  # 4->53, 5->27
        elif clock in [7, 8]:
            x = -80 + (9 - clock) * (80 / 3)  # 8->-53, 7->-27
        else:
            x = 0
        
        y = 100 - (fen['position'] / graft_length) * 200
        
        circle = Circle((x, y), 8, color='red', alpha=0.7)
        ax1.add_patch(circle)
        short_name = VESSEL_SHORT_NAMES.get(fen['vessel'], fen['vessel'])
        ax1.text(x + 12, y, short_name, fontsize=10, fontweight='bold')
    
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
    st.markdown("*Printable template - Anterior view (9-12-3)*")
    
    # Calculate dimensions
    circumference = np.pi * graft_diameter
    half_circ = circumference / 2  # We show half the circumference (9 to 3 via 12)
    
    # Create 2D template
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    
    # Draw template rectangle (showing 9 to 3 via 12 = half circumference)
    rect = Rectangle((0, 0), half_circ, graft_length, 
                    linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax2.add_patch(rect)
    
    # Clock position markers - evenly spaced from 9 to 3
    # 9=0, 10=1/6, 11=2/6, 12=3/6(center), 1=4/6, 2=5/6, 3=6/6
    clock_labels = [9, 10, 11, 12, 1, 2, 3]
    for i, clock in enumerate(clock_labels):
        x = (i / 6) * half_circ
        if clock in [9, 12, 3]:
            ax2.axvline(x=x, color='blue', linestyle='--', linewidth=1.5, alpha=0.7)
            ax2.text(x, graft_length + 5, str(clock), fontsize=11, ha='center', color='blue', fontweight='bold')
        else:
            ax2.axvline(x=x, color='lightblue', linestyle=':', linewidth=1, alpha=0.5)
            ax2.text(x, graft_length + 5, str(clock), fontsize=9, ha='center', color='gray')
    
    # Draw fenestrations
    for i, fen in enumerate(st.session_state.fenestrations):
        clock = fen['clock']
        
        # Calculate x position based on clock
        # Only show fenestrations from 9 to 3 (via 12) on this template
        if clock == 9:
            x_frac = 0
        elif clock == 10:
            x_frac = 1/6
        elif clock == 11:
            x_frac = 2/6
        elif clock == 12:
            x_frac = 3/6
        elif clock == 1:
            x_frac = 4/6
        elif clock == 2:
            x_frac = 5/6
        elif clock == 3:
            x_frac = 6/6
        elif clock == 4:
            x_frac = 7/6  # Slightly beyond 3
        elif clock == 5:
            x_frac = 8/6
        elif clock == 6:
            x_frac = 9/6  # Far right (posterior)
        elif clock == 7:
            x_frac = -2/6  # Far left (posterior)
        elif clock == 8:
            x_frac = -1/6
        else:
            x_frac = 3/6
        
        x = x_frac * half_circ
        y = graft_length - fen['position']
        
        circle = Circle((x, y), fenestration_size/2, color='red', alpha=0.7)
        ax2.add_patch(circle)
        short_name = VESSEL_SHORT_NAMES.get(fen['vessel'], fen['vessel'])
        ax2.text(x + fenestration_size/2 + 2, y, short_name, fontsize=10, fontweight='bold')
    
    ax2.set_aspect('equal')
    ax2.set_xlim(-10, half_circ + 20)
    ax2.set_ylim(-5, graft_length + 15)
    ax2.set_xlabel('Circumference (mm) - Anterior Half')
    ax2.set_ylabel('Distance from Bottom (mm)')
    ax2.set_title('Printable Template (9 → 12 → 3)')
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
st.markdown("""
| Clock | Template Position |
|-------|-------------------|
| 9 | Left edge |
| 10 | Between 9 and 11 |
| 11 | Between 10 and 12 |
| **12** | **Center (Anterior)** |
| 1 | Between 12 and 2 |
| 2 | Between 1 and 3 |
| 3 | Right edge |
| 4-5 | Beyond right edge |
| 6 | Posterior (not shown) |
| 7-8 | Beyond left edge |
""")

# Print instructions
st.subheader("📄 Print Instructions")
st.info("""
1. Ensure printer is set to "Actual Size" or "100%" scale
2. This template shows the ANTERIOR half (9 to 3 via 12)
3. Align 12 o'clock mark with anterior midline of graft
4. 9 o'clock = patient's RIGHT side
5. 3 o'clock = patient's LEFT side
""")

# Download template
if st.session_state.fenestrations:
    fig_download, ax_download = plt.subplots(figsize=(12, 10))
    
    circumference = np.pi * graft_diameter
    half_circ = circumference / 2
    
    rect = Rectangle((0, 0), half_circ, graft_length, 
                    linewidth=2, edgecolor='black', facecolor='white')
    ax_download.add_patch(rect)
    
    # Clock markers
    clock_labels = [9, 10, 11, 12, 1, 2, 3]
    for i, clock in enumerate(clock_labels):
        x = (i / 6) * half_circ
        ax_download.axvline(x=x, color='blue', linestyle='--', linewidth=1, alpha=0.5)
        ax_download.text(x, graft_length + 5, f"{clock}", fontsize=9, ha='center', color='blue')
    
    for i, fen in enumerate(st.session_state.fenestrations):
        clock = fen['clock']
        if clock == 9:
            x_frac = 0
        elif clock == 10:
            x_frac = 1/6
        elif clock == 11:
            x_frac = 2/6
        elif clock == 12:
            x_frac = 3/6
        elif clock == 1:
            x_frac = 4/6
        elif clock == 2:
            x_frac = 5/6
        elif clock == 3:
            x_frac = 6/6
        elif clock == 4:
            x_frac = 7/6
        elif clock == 5:
            x_frac = 8/6
        else:
            x_frac = 3/6
        
        x = x_frac * half_circ
        y = graft_length - fen['position']
        circle = Circle((x, y), fenestration_size/2, color='red', alpha=0.7)
        ax_download.add_patch(circle)
        short_name = VESSEL_SHORT_NAMES.get(fen['vessel'], fen['vessel'])
        ax_download.text(x + fenestration_size/2 + 2, y, short_name, fontsize=10, fontweight='bold')
    
    ax_download.set_aspect('equal')
    ax_download.set_xlim(-5, half_circ + 15)
    ax_download.set_ylim(-5, graft_length + 15)
    ax_download.set_xlabel('Circumference (mm)')
    ax_download.set_ylabel('Distance from Bottom (mm)')
    ax_download.set_title(f'Graft Template - {graft_diameter}mm x {graft_length}mm (Anterior: 9→12→3)')
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
