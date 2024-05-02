import os
from fontTools.ttLib import TTFont

os.chdir(os.path.dirname(__file__))

input_dir = "./input"
output_dir = "./output"

os.mkdir(input_dir) if not os.path.exists(input_dir) else None
os.mkdir(output_dir) if not os.path.exists(output_dir) else None


def main():
    ttf_list: list[str] = []
    for file in os.listdir(input_dir):
        if file.endswith(".ttf") or file.endswith(".otf"):
            ttf_list.append(file)
    for ttf_file in ttf_list:
        font = TTFont(os.path.join(input_dir, ttf_file))
        name: str = font["name"].getBestFullName()  # type: ignore
        file_name = f'{name.replace(" ", "_")}.{ttf_file.split(".")[-1]}'
        #font.save(os.path.join(output_dir, file_name))
        print("Renamed:", file_name)

if __name__ == "__main__":
    main()
