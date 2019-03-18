import json
import spacy
from frames_utilities import *

nlp = spacy.load('en')

# dataset_name = "test"
# dataset_path = "data/frames/"
# output_path = "data/output/"
#
# # Read JSON file
# with open(dataset_path + "frames_" + dataset_name + ".json") as file:
#     in_data = json.load(file)

# Data source and output paths
archive_path = "frames_archive/"
data_dir = "frames_data/"

sets = ['train', 'test']

# Split into training and test sets
train_data, test_data = frames_split(archive_path, "frames")

for dataset_name in sets:

    # select current dataset
    if dataset_name == "train":
        data = train_data
    else:
        data = test_data

    dialogue_data = dict()
    dialogues = []
    num_dialogues = 0

    for obj in data:

        dialogue = dict()
        utterances = []
        num_utterances = 0

        for i in range(len(obj['turns'])):
            turn = obj['turns'][i]
            slots = dict()

            # Split into sentences
            text = nlp(turn['text'])
            for sent in text.sents:

                utterance = dict()

                # Get speaker
                if turn['author'] == "user":
                    utterance['speaker'] = "USR"
                else:
                    utterance['speaker'] = "SYS"

                    # Get the slot values for the previous user turn
                    prev_turn_args = obj['turns'][i - 1]['labels']['acts_without_refs']
                    for k in range(len(prev_turn_args)):
                        for l in range(len(prev_turn_args[k]['args'])):
                            slot_vals = prev_turn_args[k]['args'][l]
                            # Ignore the anaphora, intent and empty values
                            if slot_vals['key'] != 'ref_anaphora' and slot_vals['key'] != 'intent' and slot_vals['val'] is not None:
                                slots[slot_vals['key']] = slot_vals['val']

                # Add the utterance text
                utterance['text'] = sent.text

                # Set labels to empty
                utterance['ap_label'] = ""
                utterance['da_label'] = ""

                # Add slots data
                if turn['author'] == 'wizard':
                    utterance['slots'] = slots

                # Add to utterances
                num_utterances += 1
                utterances.append(utterance)

        # Create dialogue
        dialogue['dialogue_id'] = dataset_name + '_' + str(num_dialogues + 1)
        dialogue['num_utterances'] = num_utterances
        dialogue['utterances'] = utterances

        # Create the scenario
        scenario = dict()
        scenario['db_id'] = obj['user_id']
        scenario['db_type'] = 'booking'
        scenario['task'] = 'book'
        items = []
        # Accumulate all the search results
        for turn in obj['turns']:
            # Check we have some results
            if 'db' in turn and turn['db']['result']:
                for results in turn['db']['result']:
                    for result in results:
                        # Add to items if not already present
                        if result and result not in items:
                            items.append(result)

        scenario['items'] = items
        dialogue['scenario'] = scenario

        # Add to dialogues
        num_dialogues += 1
        dialogues.append(dialogue)

    dialogue_data['dataset'] = dataset_name
    dialogue_data['num_dialogues'] = num_dialogues
    dialogue_data['dialogues'] = dialogues

    # Write a JSON file
    save_json_data(data_dir, "frames_" + dataset_name + ".json", dialogue_data)
    # with open(output_path + "frames_" + dataset_name + "_set.json", "w+") as file:
    #     json.dump(dialogue_data, file, sort_keys=False, indent=4, separators=(',', ': '))