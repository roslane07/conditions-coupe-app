"""
Module for loading and validating data files.
Handles JSON and CSV data loading with proper error handling and caching.
"""

import json
import os
from typing import Dict, List, Any
import streamlit as st

class DataLoader:
    """Class for loading and caching data files."""
    
    @staticmethod
    @st.cache_data
    def load_json(file_path: str) -> Dict[str, Any]:
        """
        Load and cache JSON data from a file.
        
        Args:
            file_path (str): Path to the JSON file
            
        Returns:
            Dict[str, Any]: Loaded JSON data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in file {file_path}: {str(e)}", e.doc, e.pos)
            
    @staticmethod
    def validate_machine_capacities(data: List[Dict[str, float]]) -> bool:
        """
        Validate machine capacities data structure.
        
        Args:
            data (List[Dict[str, float]]): Machine capacities data
            
        Returns:
            bool: True if data is valid
            
        Raises:
            ValueError: If data structure is invalid
        """
        if not isinstance(data, list):
            raise ValueError("Machine capacities must be a list")
            
        required_fields = {"n", "power", "torque"}
        for record in data:
            if not isinstance(record, dict):
                raise ValueError("Each record must be a dictionary")
            if not all(field in record for field in required_fields):
                raise ValueError(f"Each record must contain fields: {required_fields}")
            if not all(isinstance(record[field], (int, float)) for field in required_fields):
                raise ValueError("All values must be numbers")
                
        return True
        
    @staticmethod
    def validate_cutting_conditions(data: Dict[str, Any]) -> bool:
        """
        Validate cutting conditions data structure.
        
        Args:
            data (Dict[str, Any]): Cutting conditions data
            
        Returns:
            bool: True if data is valid
            
        Raises:
            ValueError: If data structure is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Cutting conditions must be a dictionary")
            
        required_fields = {"Vc", "fn", "ap", "ae", "kc1", "m0", "Y0"}
        for tool_type, conditions in data.items():
            if not isinstance(conditions, dict):
                raise ValueError(f"Conditions for {tool_type} must be a dictionary")
            if not all(field in conditions for field in required_fields):
                raise ValueError(f"Each tool type must contain fields: {required_fields}")
            if not all(isinstance(conditions[field], (int, float)) for field in required_fields):
                raise ValueError("All values must be numbers")
                
        return True 