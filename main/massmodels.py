from openai import OpenAI
import os
import re 
import tqdm
import shelve

client = OpenAI(organization="")

# a quick function to look up any files in any directories for the model
find_file = lambda filename, modeldir : os.path.join([dirpath for dirpath, dirnames, filenames in modeldir if filename in filenames][0], filename)

model_types = [".hoc", ".py", ".m", ".ode", ".c", ".f"]

nrnlib = sum([files for dictpath, dictname, files in os.walk("nrn_lib")], [])

class ModelFiles():
    def __init__(self, model_num):
        self.modelnum = model_num
        self.model_directory = list(os.walk(f"mass_models\\{self.modelnum}"))
        self.allfiles = sum([filenames for dirpath, dirnames, filenames in self.model_directory], [])
        self.model_type = []
        for file in self.allfiles:
            self.model_type += [ext for ext in self.model_type if file.endswith(ext)]
        self.model_type = set(self.model_type)
        self.all_relevant_files = [filename for filename in self.allfiles if re.search(r"(?!mosinit).*(\.hoc|\.py|\.mod|\.m|\.c|\.ode|\.f)", filename)]

    def mosinit(self): # retrieve all files in mosinit.hoc
        if "mosinit.hoc" in self.allfiles:
            mosinit_path = find_file("mosinit.hoc", self.model_directory)
            with open(mosinit_path) as file:
                text = file.read()
            self.mosinit_files = re.findall(r'(?:load_file|xopen)\( *"(?!nrngui\.hoc)(.*)" *\)', text)
            self.mosinit_files = [filename for filename in self.mosinit_files if filename not in nrnlib]
        else:
            self.mosinit_files = []
        return self.mosinit_files

    def figfiles(self): # retrieve all files that start with 'fig'
        self.fig_files = [filename for filename in self.allfiles if re.search(r"(^fig).*(\.hoc|\.py|\.m|\.c|\.ode|\.f)", filename)]
        return self.fig_files
    
    def modfiles(self): # retrieve all files in the .mod format
        self.mod_files = [filename for filename in self.allfiles if re.search(r".*(\.mod)", filename)]
        return self.mod_files
    
    def mostchars(self): # retrieve file with most characters
        chars = []
        for filename in self.all_relevant_files:
            with open(find_file(filename, self.model_directory), errors="ignore") as file:
                file_text = file.read()
                chars.append(len(file_text))
        if chars:
            return [self.all_relevant_files[chars.index(max(chars))]]
        return []
    
    def mostcomments(self): # retrieve file with most comments
        comments = []
        for filename in self.all_relevant_files:
            with open(find_file(filename, self.model_directory), errors="ignore") as file:
                file_text = file.read()
                if filename.endswith(".hoc") or filename.endswith(".c"):
                    comments.append(len(re.findall(r'((//.*)|(/\*.*\*/))', file_text)))
                if filename.endswith(".py") or filename.endswith(".ode"):
                    comments.append(len(re.findall(r'((\#.*)|(\"\"\".*\"\"\"))', file_text)))
                if filename.endswith(".m"):
                    comments.append(len(re.findall(r'((\%.*)|(\%\{.*\%\}))', file_text)))
                if filename.endswith(".f"):
                    comments.append(len(re.findall(r'^c .*', file_text)))
        if comments:
            return [self.all_relevant_files[comments.index(max(comments))]]
        return []
    
    def readme(self): # any readme files?
        return [filename for filename in self.allfiles if "readme" in filename.lower()]

data_structure = { # the data structure GPT should respond in
    "file name": "the name of the file you're analyzing, str",
    "cell types": [list],
    "currents": [list],
    "genes": [list],
    "model concept": [list],
    "model type": [list],
    "receptors": [list],
    "regions": [list],
    "simulator environment": [list],
    "transmitters": [list],
    "short model description": "a short description of the model, str"
}

with open("vocabularygpt.json") as file: # GPT's controlled vocabulary
    controlled_vocabulary = file.read()

model_ids = [237555, 184176, 181967, 249706, 245018, 154288, 154732, 117691, 168591, 119283, 144490, 140881, 114654, 137743, 184168, 141270, 2730, 206365, 53893, 147117, 119214, 267566, 184545, 62266, 266498, 126899, 150225, 116981, 126465, 37819, 127995, 98902, 266868, 20014, 118894, 155057, 189946, 144010, 260740, 151282, 3677, 226422, 57905, 148644, 83562, 145917, 188543, 235052, 2017006, 136773, 37129, 2014996, 228604, 184196, 206310, 184344, 150288, 267047, 227114, 2014816, 155727, 184339, 228337, 239039, 144403, 118554, 167694, 245879, 266823, 152292, 126098, 258235, 184325, 234118, 146949, 267048, 150031, 3807, 118261, 181962, 33728, 156470, 266864, 118020, 183718, 266687, 150678, 64296, 8284, 87582, 266806, 256628, 267307, 190304]

for model_id in tqdm.tqdm(model_ids):
    model = ModelFiles(model_id)
    compilation = {"Mosinit Files": model.mosinit(), "Files starting with Fig": model.figfiles(), "Mod Files": model.modfiles(), "File with most characters": model.mostchars(), "File with most comments": model.mostcomments(), "README Files": model.readme()}

    prompt = f"I've given you one of the code files of model {model_id} above. Infer the biological properties of the model given one of its code. Answer with this data structure given in JSON - {data_structure}. I've given a controlled vocabulary sheet below, if the field of the data structure matches the one in the controlled vocabulary, you should only pick from there and nothing else. Feel free to pick more than one item from the controlled vocabulary if needed."

    with shelve.open("massgpt_data") as data:
        for category, filelist in compilation.items():
            if not filelist:
                continue # skip if model doesn't contain any files in the category (e.g. it's a python model thus wouldn't have mosinit files)
            for filename in filelist:
                with open(find_file(filename, model.model_directory), errors="ignore") as file:
                    content = file.read()
                if len(content) > 12000: 
                    content = content[0:12000] # if file exceeds 12k chars, shorten it down to reduce token size.
                for i in range(3): # prompt GPT three times
                    if "currents" not in data[f'{model_id}/{category}/{i+1}/{filename}']:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You're a helpful assistant that analyzes neuronal model code for users. If given a data structure, answer in JSON with the data structure."
                                },
                                {
                                    "role": "user",
                                    "content": f'"File name: \n{filename}\n\nContent: \n{content}'
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                },
                                {
                                    "role": "user",
                                    "content": controlled_vocabulary
                                }
                            ],
                            response_format={"type":"json_object"}
                        ) 
                        data[f'{model_id}/{category}/{i+1}/{filename}'] = response.choices[0].message.content


print("\n\nProgram completed with no errors.")