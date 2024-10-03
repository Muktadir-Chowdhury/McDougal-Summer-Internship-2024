import re 
import os

# a quick function to look up any files in any directories for the model
find_file = lambda filename, modeldir : os.path.join([dirpath for dirpath, dirnames, filenames in modeldir if filename in filenames][0], filename)

class ModelFiles():
    def __init__(self, model_num):
        self.modelnum = model_num
        self.model_directory = list(os.walk(f"models\\{self.modelnum}"))
        self.allhocpy_files = [filename for filename in sum([filenames for dirpath, dirnames, filenames in self.model_directory], []) if re.search(r"(?!mosinit).*(\.hoc|\.py)", filename)]
        self.modhocpy_files = self.allhocpy_files + self.modfiles()
        self.hoc_format = bool(self.mosinit()) # Is it a .hoc or a .py model?

    def mosinit(self):
        try:
            mosinit_path = find_file("mosinit.hoc", self.model_directory)
            with open(mosinit_path) as file:
                text = file.read()
            self.mosinit_files = re.findall(r'(?:load_file|xopen)\( *"(?!nrngui\.hoc)(.*)" *\)', text)
        except IndexError:
            self.mosinit_files = []
        return self.mosinit_files
    
    def figfiles(self):
        self.fig_files = [filename for filename in sum([filenames for dirpath, dirnames, filenames in self.model_directory], []) if re.search(r"(^fig).*(\.hoc|\.py)", filename)]
        return self.fig_files
    
    def modfiles(self):
        self.mod_files = [filename for filename in sum([filenames for dirpath, dirnames, filenames in self.model_directory], []) if re.search(r".*(\.mod)", filename)]
        return self.mod_files
    
    def mostchars(self):
        chars = []
        for filename in self.modhocpy_files:
            with open(find_file(filename, self.model_directory)) as file:
                file_text = file.read()
                chars.append(len(file_text))
        return self.modhocpy_files[chars.index(max(chars))]
    
    def mostcomments(self):
        comments = []
        for filename in self.modhocpy_files:
            with open(find_file(filename, self.model_directory)) as file:
                file_text = file.read()
                if self.hoc_format:
                    comments.append(len(re.findall(r'(//.*)', file_text)))
                else:
                    comments.append(len(re.findall(r'((\#.*)|(\"\"\".*\"\"\"))', file_text)))
        return self.modhocpy_files[comments.index(max(comments))]

model = ModelFiles(2017143)
print(f"Model Format: {'.hoc' if model.hoc_format else '.py'}\nMosinit Files: {model.mosinit()}\nFig Files: {model.figfiles()}\nMod Files: {model.modfiles()}\nFile w/ Most Characters: {model.mostchars()}\nFile w/ Most Comments: {model.mostcomments()}")
