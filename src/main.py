import gradio as gr

# Define the chatbot function with conversation history
def chatbot_response(message, history=[]):
    # Append the new message to the history
    history.append(f"User: {message}")
    
    # Generate a response (you can replace this with a more advanced model)
    if "hello" in message.lower():
        response = "Hello! How can I help you today?"
    elif "bye" in message.lower():
        response = "Goodbye! Have a great day!"
    else:
        response = "I'm not sure how to respond to that. Can you ask something else?"

    # Append the response to the history
    history.append(f"Bot: {response}")
    
    # Return the entire conversation history as the output
    return "\n".join(history), history

# Create a Gradio interface
with gr.Blocks() as demo:
    
    txt = gr.Textbox(label="enter you question about speeches", lines=2)
    btn = gr.Button(valufilepathe="Submit")
    outputs = [
    gr.Textbox(value="", label="generate"),
    gr.Image(type="filepath", label="images"),
    ]
    btn.click(chatbot_response, inputs=[txt], outputs=outputs)

# Launch the interface
if __name__ == "__main__":
    demo.launch()
    """_summary_
    """