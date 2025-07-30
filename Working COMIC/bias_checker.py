def check_prompt_for_bias(prompt):
    bias_keywords = [
        "black", "latino", "latina", "asian", "white", "native", "brown", 
        "african", "race", "ethnicity", "person of color", "skin color"
    ]
    return any(keyword in prompt.lower() for keyword in bias_keywords)
