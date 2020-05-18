from src.thumbnail_maker import thumbnail_image, simple_filename, make_author_string
import pandas as pd
import click
import datetime
import os
import tqdm
import re

TITLE_COLUMN = "title"
ABSTRACT_COLUMN = "abstract"
AUTHOR_COLUMN_CONTAINS = "author"
THUMBNAIL_DIRECTORY = "thumbnail_images"
MIN_HEIGHT = 570
WIDTH = 1000


@click.command()
@click.option("--filename", "-f")
@click.option("--min_height", "-h", default=MIN_HEIGHT)
@click.option("--width", "-w", default=WIDTH)
@click.option("--title_column", "-T", default=TITLE_COLUMN)
@click.option("--abstract_column", "-A", default=ABSTRACT_COLUMN)
@click.option("--author_column_contains", "-au", default=AUTHOR_COLUMN_CONTAINS)
@click.option("--thumbnail_directory", "-d", default=THUMBNAIL_DIRECTORY)
@click.option("--use_oxford", "-ox", default=False)
def generate_thumbnails(
    filename,
    min_height,
    width,
    title_column,
    abstract_column,
    author_column_contains,
    thumbnail_directory,
    use_oxford,
):
    data = pd.read_csv(filename)

    author_columns = []
    for c in data.columns:
        if re.match(author_column_contains, c) is not None:
            author_columns.append(c)

    author_list = []
    for _, row in data[author_columns].iterrows():
        auths = row[~pd.isna(row)].tolist()
        author_list.append(make_author_string(auths, use_oxford=use_oxford))

    title_list = data[title_column].tolist()
    abstract_list = data[abstract_column].tolist()

    if not os.path.exists(thumbnail_directory):
        os.mkdir(thumbnail_directory)

    batch_dir = f"batch_{str(datetime.date.today()).replace('-', '_')}"
    if not os.path.exists(f"{thumbnail_directory}/{batch_dir}"):
        os.mkdir(f"{thumbnail_directory}/{batch_dir}")

    for title, authors, abstract in tqdm.tqdm(
        zip(title_list, author_list, abstract_list), total=len(title_list)
    ):
        img = thumbnail_image(
            title, authors, abstract, image_width=width, min_height=min_height
        )
        fname = simple_filename(
            title, f"{thumbnail_directory}/{batch_dir}", max_words=8
        )
        img.save(
            fname, dpi=(150, 150),
        )

    return


if __name__ == "__main__":
    generate_thumbnails()
