from app.services.retrieval.metadata_extractor import extract_metadata

problem = """
Given an array of integers nums and an integer target,
return the indices of two numbers such that they add up to target.
"""

metadata = extract_metadata(problem)

print(metadata)