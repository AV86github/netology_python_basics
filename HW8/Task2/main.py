import os


def get_line_count(file):
    with open(file) as f:
        return len(f.readlines())


def main():
    files = [x for x in os.listdir(os.getcwd()) if not x.endswith("py")]
    files_dict = {}
    for file in files:
        files_dict.setdefault(file, get_line_count(file))
    # sort dict by line count
    files_dict = dict(sorted(files_dict.items(), key=lambda x: x[1]))
    print(files_dict)
    with open("res.txt", "w") as f:
        for file, line_count in files_dict.items():
            f.write(f"{file}\n{line_count}\n")
            with open(file) as f1:
                f.write(f1.read())
            f.write("\n")


if __name__ == "__main__":
    main()
