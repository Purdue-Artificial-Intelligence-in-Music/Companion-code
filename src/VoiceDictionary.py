#add new voice command entries to the system, interpret input phrases by matching them with 
#the appropriate commands, and execute the corresponding functions tied to those commands.
from VoiceDictionaryEntry import VoiceDictionaryEntry
class VoiceDictionary:
    def __init__(self):
        self.entries = []

    def add_command(self, command_name, similar_words, function_to_call):
        new_entry = VoiceDictionaryEntry(command_name, similar_words, function_to_call)
        self.entries.append(new_entry)

    def interpret_and_execute(self, input_phrase):
        for entry in self.entries:
            if entry.check_match_and_execute(input_phrase):
                return entry.command_name
        return None
