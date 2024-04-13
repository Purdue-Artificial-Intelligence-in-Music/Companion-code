class VoiceDictionaryEntry:
    def __init__(self, command_name, similar_words, function_to_call):
        self.command_name = command_name
        self.similar_words = similar_words
        self.function_to_call = function_to_call
#The VoiceDictionaryEntry class represents individual voice commands. 
#Each instance holds a command name, a list of similar words or phrases that could trigger the command, 
#and a function to call when the command is recognized. 
#The class includes a method to check if a given input phrase matches any of the similar words. 
#If there's a match, the associated function is executed, making it a crucial component for 
#interpreting and acting on voice commands within the system.        

    def check_match_and_execute(self, input_phrase):
        if any(similar_word in input_phrase for similar_word in self.similar_words):
            self.function_to_call()
            return True
        return False