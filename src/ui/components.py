"""
Module for UI components.
Contains reusable Streamlit components with consistent styling and error handling.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go

class UIComponents:
    """Class for reusable UI components."""
    
    @staticmethod
    def setup_page():
        """Setup the page configuration and styling."""
        st.set_page_config(
            page_title="Conditions de coupe",
            page_icon="🔧",
            layout="wide"
        )
        
        st.markdown("""
        <style>
            html, body, [class*="css"] {
                font-family: 'Roboto', sans-serif !important;
            }
            .stButton>button {
                width: 100%;
            }
            .stNumberInput>div>div>input {
                text-align: right;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.title("Calcul automatique des conditions de coupe")
        
    @staticmethod
    def machine_parameters_sidebar() -> Dict[str, float]:
        """
        Create the machine parameters sidebar.
        
        Returns:
            Dict[str, float]: Dictionary containing max_power and max_torque
        """
        st.sidebar.header("⚙️ Paramètres machine global")
        return {
            "max_power": st.sidebar.number_input(
                "Puissance max (kW)",
                value=10.5,
                step=0.1,
                min_value=0.1
            ),
            "max_torque": st.sidebar.number_input(
                "Couple max (Nm)",
                value=95.0,
                step=1.0,
                min_value=0.1
            )
        }
        
    @staticmethod
    def tool_selection(available_tools: List[str]) -> str:
        """
        Create the tool selection dropdown.
        
        Args:
            available_tools (List[str]): List of available tool types
            
        Returns:
            str: Selected tool type
        """
        return st.sidebar.selectbox(
            "Choisir une plaquette",
            available_tools
        )
        
    @staticmethod
    def display_results(results: Dict[str, float], machine_params: Dict[str, float]):
        """
        Display calculation results with proper formatting.
        
        Args:
            results (Dict[str, float]): Dictionary of calculation results
            machine_params (Dict[str, float]): Machine parameters
        """
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Résultats de calcul")
            for key, value in results.items():
                st.metric(
                    label=key,
                    value=f"{value:.2f}",
                    delta=None
                )
                
        with col2:
            st.subheader("Capacités machine")
            for key, value in machine_params.items():
                st.metric(
                    label=key,
                    value=f"{value:.2f}",
                    delta=None
                )
                
    @staticmethod
    def plot_capacity_curve(machine_caps: List[Dict[str, float]]):
        """
        Plot the machine capacity curve.
        
        Args:
            machine_caps (List[Dict[str, float]]): Machine capacity data
        """
        if not machine_caps:
            return
            
        # Sort data by rotation speed
        caps = sorted(machine_caps, key=lambda x: x["n"])
        ns = [cap["n"] for cap in caps]
        powers = [cap["power"] for cap in caps]
        torques = [cap["torque"] for cap in caps]
        
        # Create figure
        fig = go.Figure()
        
        # Add power curve
        fig.add_trace(go.Scatter(
            x=ns,
            y=powers,
            name="Puissance (kW)",
            line=dict(color="blue")
        ))
        
        # Add torque curve
        fig.add_trace(go.Scatter(
            x=ns,
            y=torques,
            name="Couple (Nm)",
            line=dict(color="red"),
            yaxis="y2"
        ))
        
        # Update layout
        fig.update_layout(
            title="Courbes de capacité machine",
            xaxis_title="Vitesse de rotation (tr/min)",
            yaxis_title="Puissance (kW)",
            yaxis2=dict(
                title="Couple (Nm)",
                overlaying="y",
                side="right"
            ),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    @staticmethod
    def error_message(message: str):
        """
        Display an error message in a consistent format.
        
        Args:
            message (str): Error message to display
        """
        st.error(f"⚠️ {message}")
        
    @staticmethod
    def success_message(message: str):
        """
        Display a success message in a consistent format.
        
        Args:
            message (str): Success message to display
        """
        st.success(f"✅ {message}")
        
    @staticmethod
    def warning_message(message: str):
        """
        Display a warning message in a consistent format.
        
        Args:
            message (str): Warning message to display
        """
        st.warning(f"⚠️ {message}") 