import logging
import subprocess
import extract_text

from pathlib import Path


def convert_to_text(indir):
    for i in indir.iterdir():
        if i.is_dir():
            convert_to_text(i)
        elif i.name == ".DS_Store":
            pass
        else:
            new_parts = i.parts[2:len(i.parts)-1]
            new_path = Path("data/clean/" + "/".join(new_parts))
            outfile = new_path.joinpath(i.stem + ".txt")
            if not new_path.exists():
                new_path.mkdir(parents=True)
            if not Path(outfile).exists():
                try:
                    # print("Looking at " + str(new_path))
                    # print(i)
                    text = extract_text.extract_text_from_file(i)
                except subprocess.CalledProcessError:
                    logging.error('Problem extracting file: {}'.format(i))
                    continue
                with outfile.open('w', encoding='utf-8') as outf:
                    outf.write(text)


convert_to_text(Path("data/raw"))
