"""
duckdb_wrangle.py

Data wrangling module for Project 4: Nepal Earthquake Damage Prediction.
This module provides functions to query CSV data using DuckDB for machine learning classification tasks.

Usage:
    from duckdb_wrangle import wrangle_nepal_data

    # All data (default)
    df = wrangle_nepal_data("./data")

    # Specific district (e.g., Gorkha = district_id 4)
    df_gorkha = wrangle_nepal_data("./data", district_id=4)
"""

import duckdb
import pandas as pd


def wrangle_nepal_data(csv_path="./data", district_id=None):
    """
    Retrieve and prepare Nepal earthquake data for binary classification.

    This function reads CSV files using DuckDB and joins building structure
    with building damage data. The damage_grade column is kept as-is for use
    in creating the target variable in Lesson 2.

    Parameters:
    -----------
    csv_path : str
        Path to the data folder (default: "./data")
    district_id : int, optional
        Filter by specific district (e.g., 4 for Gorkha).
        If None, returns all districts.

    Returns:
    --------
    pd.DataFrame
        DataFrame with features and damage_grade column
    """
    # Build file paths
    structure_path = f"{csv_path}/building_structure.csv"
    damage_path = f"{csv_path}/building_damage.csv"

    # Build WHERE clause
    where_clause = "WHERE b.damage_grade IS NOT NULL"
    if district_id is not None:
        where_clause += f" AND i.district_id = {district_id}"

    # Always join with id_map to get district_id
    query = f"""
        SELECT DISTINCT
            s.building_id,
            i.district_id,
            s.age_building,
            s.plinth_area_sq_ft,
            s.height_ft_pre_eq,
            s.foundation_type,
            s.ground_floor_type,
            b.damage_grade
        FROM read_csv_auto('{structure_path}') s
        JOIN read_csv_auto('{damage_path}') b ON s.building_id = b.building_id
        JOIN read_csv_auto('./data/id_map.csv') i ON s.building_id = i.building_id
        {where_clause}
    """

    return (
        duckdb.sql(query)
        .df()
        .set_index("building_id")
        .assign(
            severe_damage=lambda x: (
                x["damage_grade"]
                .str.contains("Grade 4|Grade 5")
                .fillna(False)
                .astype(int)
            )
        )
        .drop(columns=["damage_grade"])
    )
