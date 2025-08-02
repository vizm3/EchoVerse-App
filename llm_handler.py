# llm_handler.py
import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Use caching to load the model and tokenizer only once
@st.cache_resource
def load_model():
    """
    Loads the pre-trained IBM Granite model and tokenizer from Hugging Face.
    The `st.cache_resource` decorator ensures this function is run only once.
    """
    model_id = "ibm-granite/granite-3.2-2b-instruct"
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto" # Requires the 'accelerate' library
    )
    return tokenizer, model

def create_prompt(text, tone):
    """
    Creates a specific, constrained instruction-based prompt for the model.
    """
    # Added stricter instructions to preserve meaning and avoid adding new content.
    base_instruction = "IMPORTANT: Do not add any new information, characters, or events. The rewritten text must contain ONLY the information present in the original text."

    prompts = {
        "Neutral": f"Rewrite the following text in a clear, objective, and neutral tone. {base_instruction}\n\nOriginal Text: \"{text}\"\n\nRewritten Text:",
        "Suspenseful": f"Transform the following text into a suspenseful and thrilling narrative. Build tension and a sense of mystery. {base_instruction}\n\nOriginal Text: \"{text}\"\n\nRewritten Text:",
        "Inspiring": f"Rewrite the following text to be inspiring and motivational. Use powerful and uplifting language. {base_instruction}\n\nOriginal Text: \"{text}\"\n\nRewritten Text:"
    }
    return prompts.get(tone, prompts["Neutral"])

def rewrite_text(text, tone):
    """
    Rewrites the input text using the IBM Granite model with controlled generation.
    """
    try:
        tokenizer, model = load_model()
        
        prompt = create_prompt(text, tone)
        
        model_inputs = tokenizer(prompt, return_tensors="pt")

        # **FIX:** Control output length to be proportional to input length.
        # This prevents the model from generating excessive new content.
        # It allows for up to 50% more tokens than the input, with a cap of 512.
        input_token_length = model_inputs["input_ids"].shape[1]
        max_new = min(512, int(input_token_length * 1.2))


        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_new,
            do_sample=True,
            top_p=0.9,
            temperature=0.65, # Lowered temperature for more focused output
            repetition_penalty=1.1, # Discourage repeating the same phrases
            pad_token_id=tokenizer.eos_token_id
        )
        
        # Decode only the newly generated tokens for a cleaner output.
        input_length = model_inputs["input_ids"].shape[1]
        new_tokens = generated_ids[0, input_length:]
        rewritten_part = tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        return rewritten_part

    except Exception as e:
        st.error(f"An error occurred during text rewriting: {e}")
        print(f"Error details: {e}")
        return "Failed to rewrite text. Please check the logs."
