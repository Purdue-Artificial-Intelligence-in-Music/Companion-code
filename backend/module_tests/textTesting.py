from transformers import pipeline

# Initialize the zero-shot classification pipeline with the Roberta model
classifier = pipeline("zero-shot-classification", model="roberta-large-mnli")

# Define the list of possible commands along with hypothesis templates
commands = {
    "speed up": "The action involves increasing speed.",
    "slow down": "The action involves decreasing speed.",
    "volume up": "The action involves increasing volume.",
    "volume down": "The action involves decreasing volume.",
    "stop": "The action involves bringing something to a halt.",
    "start": "The action involves beginning something.",
    "exit": "The action involves the termination of something.",
    # "edit": "The action involves changing something."
    "deafen": "The action involves the termination of listening",
}


# Enhance the classify_command function to handle a wider range of negations
def classify_command(user_input):
    # Check for negations and adjust the command accordingly
    negations = ["don't", "do not", "please don't", "never", "no", "not"]
    # Adjustments for negations
    adjustments = {
        "don't stop": "start",
        "do not stop": "start",
        "never stop": "start",
        "don't go": "stop",
        "do not go": "stop",
        "never go": "stop",
        "do not listen": "deafen",
        "don't listen": "deafen",
        "never listen": "deafen",
    }
    # Action phrases that directly map to commands
    action_phrases = {
        "too fast": "slow down",
        "too slow": "speed up",
        "too loud": "volume down",
        "too quiet": "volume up",
        "go": "start",
        "halt": "stop",
        "be quiet": "volume down",
        "stop playing": "stop",
        "pause": "stop",
        "I can't hear": "volume up",
        "it's noisy": "volume down",
        "return": "deafen",
    }

    # First check for any negation adjustments
    for phrase, command in adjustments.items():
        if phrase in user_input.lower():
            return command

    # Next, check for direct action phrase mappings
    for phrase, command in action_phrases.items():
        if phrase in user_input.lower():
            return command

    # If no special cases, proceed with model classification
    hypotheses = [f"The action is: {desc}" for desc in commands.values()]
    result = classifier(
        user_input, hypotheses, multi_label=True
    )  # Changed multi_class to multi_label
    highest_score = max(result["scores"])
    highest_scoring_command = [
        cmd
        for cmd, desc in commands.items()
        if f"The action is: {desc}"
        == result["labels"][result["scores"].index(highest_score)]
    ][0]
    return highest_scoring_command


if __name__ == "__main__":
    # Get the user's command as input
    user_input = input("The user command is: ")
    command = classify_command(user_input)

    # Print out the command that matches the user's input
    print(f"The closest command to the user's input is: {command}")
