import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle, Arc
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="PMEG Template Generator",
    page_icon="🏥",
    layout="wide"
)

# Logo path (local file in main directory)
LOGO_PATH = "logo.png"

# Vessel name options - REORDERED: RRA before LRA
VESSEL_OPTIONS = [
    "Celiac Trunk",
    "SMA",
    "RRA",
    "LRA",
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

# Function to convert clock position to X fraction on template
def clock_to_x_fraction(clock_position):
    if clock_position == 6:
        return 0.0
    elif clock_position == 7:
        return 1/12
    elif clock_position == 8:
        return 2/12
    elif clock_position == 9:
        return 3/12
    elif clock_position == 10:
        return 4/12
    elif clock_position == 11:
        return 5/12
    elif clock_position == 12:
        return 6/12
    elif clock_position == 1:
        return 7/12
    elif clock_position == 2:
        return 8/12
    elif clock_position == 3:
        return 9/12
    elif clock_position == 4:
        return 10/12
    elif clock_position == 5:
        return 11/12
    return 0.5

# Function to check if fenestration is behind the graft (posterior side)
def is_behind_graft(clock_position):
    return clock_position in [4, 5, 6, 7, 8]

# Function to load logo from local file
@st.cache_data
def load_logo():
    try:
        img = Image.open(LOGO_PATH)
        return np.array(img)
    except:
        return None

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

# Load logo
logo_img = load_logo()

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
    
    fig1, ax1 = plt.subplots(figsize=(8, 7))
    ax1.set_xlim(-150, 160)
    ax1.set_ylim(-160, 160)
    
    # Calculate scaling factor for accurate representation
    # The graft width in the plot is 160 units (from -80 to 80)
    # This represents the graft diameter in mm
    scale_factor = 160 / graft_diameter  # units per mm
    
    # Draw top ellipse - FILLED completely with graft color (not visible from front)
    ellipse_top_fill = patches.Ellipse((0, 100), 160, 60, linewidth=0, 
                                       facecolor='lightblue', alpha=0.3, zorder=1)
    ax1.add_patch(ellipse_top_fill)
    
    # Draw top ellipse - TOP HALF (solid line - visible part)
    # Top arc: from 180 to 0 degrees (left to right, upper half)
    arc_top = Arc((0, 100), 160, 60, angle=0, theta1=0, theta2=180, 
                  linewidth=2, edgecolor='black', fill=False, zorder=2)
    ax1.add_patch(arc_top)
    
    # Draw top ellipse - BOTTOM HALF (dotted line - part curving away)
    # Bottom arc: from 0 to -180 degrees (right to left, lower half)
    theta = np.linspace(0, -np.pi, 100)
    x_bottom = 80 * np.cos(theta)
    y_bottom = 100 + 30 * np.sin(theta)
    ax1.plot(x_bottom, y_bottom, 'k:', linewidth=2, alpha=0.6, zorder=2)
    
    # Draw cylinder body (sides)
    ax1.plot([-80, -80], [-100, 100], 'k-', linewidth=2.5, zorder=2)
    ax1.plot([80, 80], [-100, 100], 'k-', linewidth=2.5, zorder=2)
    
    # Draw bottom ellipse (fully visible, same color as shaft)
    ellipse_bottom = patches.Ellipse((0, -100), 160, 60, linewidth=2, 
                                   edgecolor='black', facecolor='lightblue', alpha=0.3, zorder=2)
    ax1.add_patch(ellipse_bottom)
    
    # Clock position labels
    ax1.text(0, 135, "12", fontsize=9, ha='center', va='center', color='blue', zorder=10)
    ax1.text(0, 65, "6", fontsize=9, ha='center', va='center', color='blue', zorder=10)
    ax1.text(-95, 100, "9", fontsize=9, ha='center', va='center', color='blue', zorder=10)
    ax1.text(95, 100, "3", fontsize=9, ha='center', va='center', color='blue', zorder=10)
    
    # Y-axis labels (distance from top) - dotted lines extend to numbers
    y_ticks = [0, graft_length//4, graft_length//2, 3*graft_length//4, graft_length]
    for tick in y_ticks:
        y_pos = 100 - (tick / graft_length) * 200
        # Draw gray dotted line from left edge through graft to the number
        ax1.plot([-80, 120], [y_pos, y_pos], color='gray', linestyle=':', linewidth=1, alpha=0.6, zorder=0)
        # Text label
        ax1.text(125, y_pos, f"{tick}", fontsize=9, ha='left', va='center', color='darkgreen', zorder=10)
    
    ax1.text(140, 0, "mm", fontsize=9, ha='left', va='center', color='darkgreen', rotation=90, zorder=10)
    
    # Draw fenestrations BEHIND the graft first (lower z-order)
    for i, fen in enumerate(st.session_state.fenestrations):
        if is_behind_graft(fen['clock']):
            clock = fen['clock']
            if clock == 12:
                x = 0
            elif clock == 9:
                x = -80
            elif clock == 3:
                x = 80
            elif clock == 6:
                x = 0
            elif clock in [10, 11]:
                x = -80 + (clock - 9) * (80 / 3)
            elif clock in [1, 2]:
                x = clock * (80 / 3)
            elif clock in [4, 5]:
                x = 80 - (clock - 3) * (80 / 3)
            elif clock in [7, 8]:
                x = -80 + (9 - clock) * (80 / 3)
            else:
                x = 0
            
            y = 100 - (fen['position'] / graft_length) * 200
            
            # Use the stored fenestration size for this specific fenestration
            fen_size = fen.get('size', 6)  # Default to 6 if not stored (backward compatibility)
            fen_radius_scaled = (fen_size / 2) * scale_factor
            
            # 50% transparency for fenestrations behind the graft
            circle = Circle((x, y), fen_radius_scaled, color='red', alpha=0.35, zorder=3)
            ax1.add_patch(circle)
            short_name = VESSEL_SHORT_NAMES.get(fen['vessel'], fen['vessel'])
            ax1.text(x + fen_radius_scaled + 2, y, short_name, fontsize=10, fontweight='bold', alpha=0.5, zorder=3)
    
    # Draw fenestrations IN FRONT of the graft (higher z-order)
    for i, fen in enumerate(st.session_state.fenestrations):
        if not is_behind_graft(fen['clock']):
            clock = fen['clock']
            if clock == 12:
                x = 0
            elif clock == 9:
                x = -80
            elif clock == 3:
                x = 80
            elif clock == 6:
                x = 0
            elif clock in [10, 11]:
                x = -80 + (clock - 9) * (80 / 3)
            elif clock in [1, 2]:
                x = clock * (80 / 3)
            elif clock in [4, 5]:
                x = 80 - (clock - 3) * (80 / 3)
            elif clock in [7, 8]:
                x = -80 + (9 - clock) * (80 / 3)
            else:
                x = 0
            
            y = 100 - (fen['position'] / graft_length) * 200
            
            # Use the stored fenestration size for this specific fenestration
            fen_size = fen.get('size', 6)  # Default to 6 if not stored (backward compatibility)
            fen_radius_scaled = (fen_size / 2) * scale_factor
            
            # Full opacity for fenestrations in front
            circle = Circle((x, y), fen_radius_scaled, color='red', alpha=0.7, zorder=5)
            ax1.add_patch(circle)
            short_name = VESSEL_SHORT_NAMES.get(fen['vessel'], fen['vessel'])
            ax1.text(x + fen_radius_scaled + 2, y, short_name, fontsize=10, fontweight='bold', zorder=5)
    
    ax1.text(0, 150, "TOP (Proximal) - 0mm", fontsize=10, ha='center', color='green', fontweight='bold', zorder=10)
    ax1.text(0, -145, f"BOTTOM (Distal) - {graft_length}mm", fontsize=10, ha='center', color='green', fontweight='bold', zorder=10)
    
    ax1.set_title(f"Graft: {graft_diameter}mm x {graft_length}mm")
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    # Add logo to bottom right - half size with 50% transparency
    if logo_img is not None:
        ax_logo1 = fig1.add_axes([0.80, 0.05, 0.075, 0.075])
        ax_logo1.imshow(logo_img, alpha=0.5)
        ax_logo1.axis('off')
    
    st.pyplot(fig1)
    plt.close(fig1)
    
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
        new_position = st.number_input("Position from top (mm)", 0, graft_length, 20)
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
            'clock': new_clock,
            'size': fenestration_size  # Store the size with each fenestration
        })
        st.rerun()

with col2:
    st.subheader("2D Template (Unwrapped)")
    st.markdown("*Full circumference: 6 (posterior) → 12 (anterior) → 6 (posterior)*")
    st.markdown(f"**Print Scale: 1:1 (Actual size on A4 paper)**")
    
    circumference = np.pi * graft_diameter
    
    # Set figure size to maintain accurate scale for A4 printing
    # A4 is 210mm x 297mm, we use DPI to ensure accurate sizing
    dpi = 25.4  # 1 inch = 25.4mm, so 1 DPI = 1mm
    fig_width = (circumference + 15) / 25.4  # Convert mm to inches
    fig_height = (graft_length + 25) / 25.4  # Convert mm to inches
    
    fig2, ax2 = plt.subplots(figsize=(fig_width, fig_height), dpi=100)
    
    rect = Rectangle((0, 0), circumference, graft_length, 
                    linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax2.add_patch(rect)
    
    clock_order = [6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    
    for i, clock in enumerate(clock_order):
        x = (i / 12) * circumference
        
        if clock in [12, 3, 6, 9]:
            ax2.axvline(x=x, color='blue', linestyle='--', linewidth=1.5, alpha=0.7)
            ax2.text(x, -5, str(clock), fontsize=11, ha='center', color='blue', fontweight='bold')
        else:
            ax2.axvline(x=x, color='lightblue', linestyle=':', linewidth=1, alpha=0.5)
            ax2.text(x, -5, str(clock), fontsize=9, ha='center', color='gray')
    
    for i, fen in enumerate(st.session_state.fenestrations):
        x_frac = clock_to_x_fraction(fen['clock'])
        x = x_frac * circumference
        y = fen['position']
        
        # Use the stored fenestration size for this specific fenestration
        fen_size = fen.get('size', 6)  # Default to 6 if not stored (backward compatibility)
        circle = Circle((x, y), fen_size/2, color='red', alpha=0.7)
        ax2.add_patch(circle)
        short_name = VESSEL_SHORT_NAMES.get(fen['vessel'], fen['vessel'])
        ax2.text(x + fen_size/2 + 2, y, short_name, fontsize=10, fontweight='bold')
    
    ax2.set_aspect('equal')
    ax2.set_xlim(-5, circumference + 10)
    ax2.set_ylim(graft_length + 10, -15)
    ax2.set_xlabel('Circumference (mm)', fontsize=10)
    ax2.set_ylabel('Distance from Top (mm)', fontsize=10)
    ax2.set_title(f'Printable Template - Full Circumference - Scale 1:1', fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # Add logo to bottom right - half size with 50% transparency
    if logo_img is not None:
        ax_logo2 = fig2.add_axes([0.87, 0.05, 0.06, 0.06])
        ax_logo2.imshow(logo_img, alpha=0.5)
        ax_logo2.axis('off')
    
    st.pyplot(fig2)
    plt.close(fig2)

# Fenestration list
if st.session_state.fenestrations:
    st.subheader("Fenestrations List")
    sorted_fens = sorted(enumerate(st.session_state.fenestrations), key=lambda x: x[1]['position'])
    for orig_idx, fen in sorted_fens:
        col_a, col_b = st.columns([4, 1])
        with col_a:
            behind_text = " (Behind graft)" if is_behind_graft(fen['clock']) else ""
            fen_size = fen.get('size', 6)  # Get stored size
            st.write(f"**{fen['vessel']}:** Position: {fen['position']:.1f}mm from top, Clock: {fen['clock']} o'clock, Size: {fen_size}mm{behind_text}")
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
    | RRA | Right Renal Artery |
    """)
with col_ref2:
    st.markdown("""
    | Abbreviation | Full Name |
    |--------------|-----------|
    | LRA | Left Renal Artery |
    | IMA | Inferior Mesenteric Artery |
    | F1-F5 | Custom Fenestrations |
    """)

# Clock position reference
st.subheader("🕐 Clock Position Reference")
st.markdown("""
**Template Layout (left to right):**

| 6 | 7 | 8 | 9 | 10 | 11 | **12** | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|----|----|--------|---|---|---|---|---|---|
| Posterior | | | Right | | | **Anterior** | | | Left | | | Posterior |

**Note:** Fenestrations at positions 4, 5, 6, 7, 8 o'clock appear behind the graft (shown with reduced opacity)
""")

# Print instructions
st.subheader("📄 Print Instructions")
st.info("""
1. **CRITICAL:** Set printer to "Actual Size" or "100%" scale (NOT "Fit to page")
2. Use A4 paper (210mm x 297mm)
3. Verify scale: Measure the template width - it should match the calculated circumference
4. Template shows FULL circumference (can be wrapped around graft)
5. Y-axis: 0 = TOP of graft (proximal), increasing downward
6. 12 o'clock (center) = Anterior (front of patient)
7. 6 o'clock (edges) = Posterior (back of patient)
8. All measurements are in millimeters (1:1 scale)
""")

# Download template
if st.session_state.fenestrations:
    fig_download, ax_download = plt.subplots(figsize=(14, 10))
    
    circumference = np.pi * graft_diameter
    
    rect = Rectangle((0, 0), circumference, graft_length, 
                    linewidth=2, edgecolor='black', facecolor='white')
    ax_download.add_patch(rect)
    
    clock_order = [6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    for i, clock in enumerate(clock_order):
        x = (i / 12) * circumference
        if clock in [12, 3, 6, 9]:
            ax_download.axvline(x=x, color='blue', linestyle='--', linewidth=1.5, alpha=0.7)
            ax_download.text(x, -5, f"{clock}", fontsize=10, ha='center', color='blue', fontweight='bold')
        else:
            ax_download.axvline(x=x, color='lightblue', linestyle=':', linewidth=1, alpha=0.5)
            ax_download.text(x, -5, f"{clock}", fontsize=9, ha='center', color='gray')
    
    for i, fen in enumerate(st.session_state.fenestrations):
        x_frac = clock_to_x_fraction(fen['clock'])
        x = x_frac * circumference
        y = fen['position']
        # Use the stored fenestration size for this specific fenestration
        fen_size = fen.get('size', 6)
        circle = Circle((x, y), fen_size/2, color='red', alpha=0.7)
        ax_download.add_patch(circle)
        short_name = VESSEL_SHORT_NAMES.get(fen['vessel'], fen['vessel'])
        ax_download.text(x + fen_size/2 + 2, y, short_name, fontsize=10, fontweight='bold')
    
    ax_download.set_aspect('equal')
    ax_download.set_xlim(-5, circumference + 10)
    ax_download.set_ylim(graft_length + 10, -15)
    ax_download.set_xlabel('Circumference (mm)')
    ax_download.set_ylabel('Distance from Top (mm)')
    ax_download.set_title(f'Graft Template - {graft_diameter}mm x {graft_length}mm - SCALE 1:1 - Print at 100%')
    ax_download.grid(True, alpha=0.3)
    
    # Add scale verification marks
    ax_download.text(5, graft_length + 5, f"Circumference: {circumference:.1f}mm", fontsize=9, color='red', fontweight='bold')
    ax_download.text(5, graft_length + 8, f"Graft: {graft_diameter}mm diameter x {graft_length}mm length", fontsize=9, color='blue')
    
    # Add logo to downloaded PDF - half size with 50% transparency
    if logo_img is not None:
        ax_logo_dl = fig_download.add_axes([0.88, 0.05, 0.05, 0.05])
        ax_logo_dl.imshow(logo_img, alpha=0.5)
        ax_logo_dl.axis('off')
    
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
