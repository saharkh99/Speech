
# src/utils.py

import os
from src.config import OPENAI_API_KEY, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
import openai
from neo4j import GraphDatabase

def connect_to_neo4j():
    """
    Create a Neo4j database driver instance using the environment variables.
    
    Returns:
        neo4j.GraphDatabase.driver: Neo4j driver instance.
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    return driver

def set_openai_api_key():
    
    openai.api_key = OPENAI_API_KEY


