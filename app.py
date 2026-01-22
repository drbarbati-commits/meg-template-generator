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

# Function to convert clock position to degrees
def clock_to_degrees(clock_position):
    # 12 o'clock = 180 degrees
    # Each hour = 30 degrees
    # Clock goes clockwise, so we subtract from 180
    degrees = 180 - (clock_position - 12) * 30
    if degrees < 0:
        degrees += 360
    if degrees >= 360:
        degrees -= 360
    return degrees

# Function to convert degrees to clock position
def degrees_to_clock(degrees):
    # Reverse of clock_to_degrees
    clock = 12 - (degrees - 180) / 30
    if clock <= 0:
        clock += 12
    if clock > 12:
        clock -= 12
    return clock

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
    st.markdown("*Add fenestrations using clock positions (12 o'clock = top)*")
    
    # Create 3D-like visualization
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    ax1.set_xlim(-100, 100)
    ax1.set_ylim(-150, 150)
    ax1.set_aspect('equal')
    
    # Draw cylinder (simplified 3D view)
    # Top ellipse
    ellipse_top = patches.Ellipse((0, -100), 160, 60, linewidth=2, 
                                 edgecolor='black', facecolor='lightblue', alpha=0.3)
    ax1.add_patch(ellipse_top)
    
    # Bottom ellipse
    ellipse_bottom = patches.Ellipse((0, 100), 160, 60, linewidth=2, 
                                   edgecolor='black', facecolor='lightblue', alpha=0.3)
    ax1.add_patch(ellipse_bottom)
    
    # Side lines
    ax1.plot([-80, -80], [-100, 100], 'k-', linewidth=2)
    ax1.plot([80, 80], [-100, 100], 'k-', linewidth=2)
    
    # Add clock position labels on top ellipse
    clock_labels = [12, 3, 6, 9]
    clock_x = [0, 80, 0, -80]
    clock_y = [-130, -100, -70, -100]
    for label, x, y in zip(clock_labels, clock_x, clock_y):
        ax1.text(x, y, f"{label}", fontsize=9, ha='center', va='center', color='blue')
    
    # Draw fenestrations
    for i, fen in enumerate(st.session_state.fenestrations):
        x = (fen['degrees'] / 360) * 160 - 80
        y = -100 + (fen['position'] / graft_length) * 200
        
        circle = Circle((x, y), 8, color='red', alpha=0.7)
        ax1.add_patch(circle)
        ax1.text(x + 12, y, f'F{i+1}', fontsize=10, fontweight='bold')
    
    ax1.set_title(f"Graft: {graft_diameter}mm x {graft_length}mm")
    ax1.axis('off')
    
    # Display the plot
    st.pyplot(fig1)
    plt.close(fig1)
    
    # Manual fenestration input
    st.markdown("**Add Fenestration Manually:**")
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
        new_degrees = clock_to_degrees(new_clock)
        st.session_state.fenestrations.append({
            'position': new_position,
            'clock': new_clock,
            'degrees': new_degrees
        })
        st.rerun()

with col2:
    st.subheader("2D Template (Unwrapped)")
    st.markdown("*Printable template - 12 o'clock at center*")
    
    # Create 2D template
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    
    # Calculate dimensions
    circumference = np.pi * graft_diameter
    
    # Draw template rectangle
    rect = Rectangle((0, 0), circumference, graft_length, 
                    linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax2.add_patch(rect)
    
    # Draw clock position markers
    clock_positions_template = [9, 12, 3, 6]
    for i, clock_pos in enumerate(clock_positions_template):
        x = (clock_to_degrees(clock_pos) / 360) * circumference
        ax2.axvline(x=x, color='blue', linestyle='--', linewidth=1, alpha=0.5)
        ax2.text(x, graft_length + 3, f"{clock_pos}", fontsize=9, ha='center', color='blue')
    
    # Draw fenestrations
    for i, fen in enumerate(st.session_state.fenestrations):
        x = (fen['degrees'] / 360) * circumference
        y = fen['position']
        
        circle = Circle((x, y), fenestration_size/2, color='red', alpha=0.7)
        ax2.add_patch(circle)
        ax2.text(x + fenestration_size/2 + 2, y, f'F{i+1}', fontsize=10, fontweight='bold')
    
    ax2.set_xlim(-5, circumference + 5)
    ax2.set_ylim(-5, graft_length + 15)
    ax2.set_xlabel('Circumference (mm)')
    ax2.set_ylabel('Length (mm)')
    ax2.set_title('Printable Template')
    ax2.grid(True, alpha=0.3)
    
    st.pyplot(fig2)
    plt.close(fig2)

# Fenestration list
if st.session_state.fenestrations:
    st.subheader("Fenestrations List")
    for i, fen in enumerate(st.session_state.fenestrations):
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.write(f"**F{i+1}:** Position: {fen['position']:.1f}mm from top, Clock: {fen['clock']} o'clock, Size: {fenestration_size}mm")
        with col_b:
            if st.button(f"Delete", key=f"del_{i}"):
                st.session_state.fenestrations.pop(i)
                st.rerun()

# Clock position reference
st.subheader("🕐 Clock Position Reference")
col_ref1, col_ref2 = st.columns(2)
with col_ref1:
    st.markdown("""
    | Clock | Position |
    |-------|----------|
    | 12 | Anterior (front) |
    | 3 | Left |
    | 6 | Posterior (back) |
    | 9 | Right |
    """)
with col_ref2:
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
5. Wrap template around actual graft
6. Use holes as cutting guides
""")

# Download template
if st.session_state.fenestrations:
    # Create downloadable template
    fig_download, ax_download = plt.subplots(figsize=(10, 8))
    
    circumference = np.pi * graft_diameter
    rect = Rectangle((0, 0), circumference, graft_length, 
                    linewidth=2, edgecolor='black', facecolor='white')
    ax_download.add_patch(rect)
    
    # Add clock markers
    for clock_pos in [9, 12, 3, 6]:
        x = (clock_to_degrees(clock_pos) / 360) * circumference
        ax_download.axvline(x=x, color='blue', linestyle='--', linewidth=1, alpha=0.5)
        ax_download.text(x, graft_length + 3, f"{clock_pos} o'clock", fontsize=9, ha='center', color='blue')
    
    for i, fen in enumerate(st.session_state.fenestrations):
        x = (fen['degrees'] / 360) * circumference
        y = fen['position']
        circle = Circle((x, y), fenestration_size/2, color='red', alpha=0.7)
        ax_download.add_patch(circle)
        ax_download.text(x + fenestration_size/2 + 2, y, f'F{i+1}', fontsize=10, fontweight='bold')
    
    ax_download.set_xlim(-5, circumference + 5)
    ax_download.set_ylim(-5, graft_length + 15)
    ax_download.set_xlabel('Circumference (mm)')
    ax_download.set_ylabel('Length (mm)')
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
