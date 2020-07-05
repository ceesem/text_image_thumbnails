from src.thumbnail_maker import thumbnail_image, simple_filename, make_author_string
import pandas as pd
import click
import datetime
import os
import tqdm
import re
import time
from multiwrapper import multiprocessing_utils as mu

TITLE_COLUMN = "title"
ABSTRACT_COLUMN = "abstract"
AUTHOR_COLUMN_CONTAINS = "author"
TWITTER_COLUMN_CONTAINS = "twitter"
THUMBNAIL_DIRECTORY = "thumbnail_images"
MIN_HEIGHT = 570
WIDTH = 1000


@click.command()
@click.option("--filename", "-f")
@click.option("--batch_name", "-b", default=None)
@click.option("--min_height", "-h", default=MIN_HEIGHT)
@click.option("--width", "-w", default=WIDTH)
@click.option("--title_column", "-T", default=TITLE_COLUMN)
@click.option("--abstract_column", "-A", default=ABSTRACT_COLUMN)
@click.option("--author_column_contains", "-au", default=AUTHOR_COLUMN_CONTAINS)
@click.option("--twitter_column_contains", "-tw", default=TWITTER_COLUMN_CONTAINS)
@click.option("--save_author_string", "-s", default=True)
@click.option("--thumbnail_directory", "-d", default=THUMBNAIL_DIRECTORY)
@click.option("--use_oxford", "-ox", default=False)
@click.option("--n_threads", "-n", default=2)
def generate_thumbnails(
    filename,
    batch_name,
    min_height,
    width,
    title_column,
    abstract_column,
    author_column_contains,
    twitter_column_contains,
    save_author_string,
    thumbnail_directory,
    use_oxford,
    n_threads,
):
    data = pd.read_csv(filename)

    author_columns = []
    for c in data.columns:
        if re.match(author_column_contains, c) is not None:
            author_columns.append(c)

    twitter_columns = []
    if twitter_column_contains is not False:
        for c in data.columns:
            if re.match(twitter_column_contains, c) is not None:
                twitter_columns.append(c)

    author_list = []
    author_list_with_handles = []
    for ii, row in data[author_columns].iterrows():
        auths = row[~pd.isna(row)].tolist()
        author_list.append(make_author_string(auths, use_oxford=use_oxford))
        try:
            twit_row = data.iloc[ii][twitter_columns]
            handles = twit_row[~pd.isna(row).values].tolist()
            author_list_with_handles.append(
                make_author_string(auths, twitter_list=handles, use_oxford=use_oxford)
            )
        except:
            print("Twitter handles failed!")
            author_list_with_handles = author_list

    title_list = data[title_column].tolist()
    abstract_list = data[abstract_column].tolist()

    if not os.path.exists(thumbnail_directory):
        os.mkdir(thumbnail_directory)

    if batch_name is None:
        batch_dir = f"batch_{str(datetime.date.today()).replace('-', '_')}"
    else:
        batch_dir = batch_name

    if not os.path.exists(f"{thumbnail_directory}/{batch_dir}"):
        os.mkdir(f"{thumbnail_directory}/{batch_dir}")

    if n_threads > 1:
        print(f"Making all images with {n_threads} processes...")
        all_args = []
        t0 = time.time()
        for title, authors, abstract in zip(title_list, author_list, abstract_list):
            all_args.append(
                [
                    title,
                    authors,
                    abstract,
                    width,
                    min_height,
                    thumbnail_directory,
                    batch_dir,
                ]
            )
        mu.multiprocess_func(_save_data_multithreaded, all_args, n_threads=n_threads)
        print(f"\tImages produced in {time.time()-t0:.2f} s.")
    else:
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

    if save_author_string:
        data["authors_with_handles"] = author_list_with_handles
        pure_filename = os.path.split(filename)[-1]
        fn = pure_filename.split(".")
        out_name = f"{thumbnail_directory}/{batch_dir}/{fn[-2].replace('/','')}_with_tweets.csv"
        data.to_csv(out_name)
        print(f"Data saved to {out_name}")
    return


def _save_data_multithreaded(data):
    title, authors, abstract, width, min_height, thumbnail_directory, batch_dir = data
    img = thumbnail_image(
        title, authors, abstract, image_width=width, min_height=min_height
    )
    fname = simple_filename(title, f"{thumbnail_directory}/{batch_dir}", max_words=8)
    img.save(
        fname, dpi=(150, 150),
    )


if __name__ == "__main__":
    generate_thumbnails()
