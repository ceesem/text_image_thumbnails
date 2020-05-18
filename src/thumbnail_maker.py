import os
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont

try:
    FONT_DIRS = {
        "library": "/Library/Fonts/",
        "user": os.path.expanduser("~/Library/Fonts/"),
        "system": "/System/Library/Fonts/",
    }
except:
    pass

DEFAULT_FONT = "Avenir.ttc"
DEFAULT_FONT_LOCATION = FONT_DIRS["system"]


def simple_filename(title, img_dir, max_words=10):
    title = re.sub("[^A-Za-z0-9\s]+", "", title.lower())
    title_l = title.split(" ")
    title_s = "_".join(title_l[0:max_words])
    return f"{img_dir}/{title_s}.png"


def make_author_string(author_list, use_oxford=True):
    if len(author_list) == 1:
        return author_list[0]
    if len(author_list) == 2:
        use_oxford = False
    author_string_front = ", ".join(author_list[:-1])
    author_string = (
        f"{author_string_front}{',' if use_oxford else ''} and {author_list[-1]}"
    )
    return author_string


def build_fonts(
    font_name,
    font_location,
    size=18,
    title_size=20,
    title_index=2,
    author_index=1,
    regular_index=0,
):
    """Get image fonts for each section

    Parameters
    ----------
    font_name : str
        Name of the font file with extension
    font_location : str
        Directory of the font
    size : int, optional
        Typeface size for regular text and authors, by default 18
    title_size : int, optional
        Typeface size for titles, by default 20
    title_index : int, optional
        Title style index for the font. 1 is usually bold or italic, with 2 and above being other styles.
        Try other numbers if you're not seeing the style you want. By default 1.
    author_index : int, optional
        Author style index for the font, by default 2
    regular_index : int, optional
        Regular text style index for the font, by default 0

    Returns
    -------
    ImageFont, ImageFont, ImageFont
        title font, author font, and text font
    """
    font_loc = f"{font_location}{font_name}"
    fnt_title = ImageFont.truetype(
        font_loc, size=title_size, index=title_index, encoding="utf-8"
    )
    fnt_author = ImageFont.truetype(
        font_loc, size=size, index=author_index, encoding="utf-8"
    )
    fnt_text = ImageFont.truetype(
        font_loc, size=size, index=regular_index, encoding="utf-8"
    )
    return fnt_title, fnt_author, fnt_text


def join_words(line):
    return " ".join(line)


def split_lines(txt, fnt, width, padding):
    w = width - 2 * padding

    split_text = txt.split(" ")
    lines = []
    new_line = []
    for word in split_text:
        try_new_line = fnt.getsize(join_words(new_line + [word] + [" "]))
        if try_new_line[0] <= w:
            new_line.append(word)
        else:
            lines.append(join_words(new_line) + "\n")
            new_line = [word]
    lines.append(join_words(new_line))
    return lines


def centered_box_corner(lines, fnt, width):
    bbox_width = fnt.getsize_multiline(join_words(lines))[0]
    right_corner = width / 2 - bbox_width / 2
    return right_corner


def image_height(text_fonts, v_padding, p_spacing):
    h = v_padding
    pts = []
    base_h = v_padding
    for txt, fnt, spc in text_fonts:
        pts.append(base_h)
        base_h += fnt.getsize_multiline(txt, spacing=spc)[1]
        base_h += p_spacing
    h += base_h - p_spacing
    return h, pts


def assemble_image(
    text_font_ctr_spacing, width, w_padding, v_padding, section_spacing, min_height
):
    lines_each = []
    fnts_each = []
    x_pts = []
    centered_each = []
    spacing_each = []
    for text, fnt, is_centered, spacing in text_font_ctr_spacing:
        lines = split_lines(text, fnt, width, w_padding)
        lines_each.append("".join(lines))
        fnts_each.append(fnt)
        centered_each.append(is_centered)
        if is_centered:
            w_corner = centered_box_corner(lines, fnt, width)
        else:
            w_corner = w_padding
        x_pts.append(w_corner)
        spacing_each.append(spacing)

    text_fonts = [(l, f, s) for l, f, s in zip(lines_each, fnts_each, spacing_each)]
    h_all, h_each = image_height(text_fonts, v_padding, section_spacing,)
    if min_height is not None:
        h_all = max([h_all, min_height])

    img = Image.new("RGB", size=(width, h_all), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    align_lookup = {True: "center", False: "left"}
    for line, fnt, is_centered, spacing, x, y in zip(
        lines_each, fnts_each, centered_each, spacing_each, x_pts, h_each
    ):
        d.multiline_text(
            (x, y),
            "".join(line),
            font=fnt,
            align=align_lookup[is_centered],
            fill=(0, 0, 0),
            spacing=spacing,
        )
    return img


def thumbnail_image(
    title,
    authors,
    abstract,
    font_name=DEFAULT_FONT,
    font_location=DEFAULT_FONT_LOCATION,
    font_size=18,
    title_size=20,
    title_font_style=2,
    author_font_style=1,
    text_font_style=0,
    line_spacing=10,
    image_width=1000,
    horizontal_padding=50,
    vertical_padding=50,
    section_spacing=25,
    min_height=None,
):
    """Generate a thumbnail image of specified text.

    Parameters
    ----------
    title : str 
        Title text without newlines
    authors : str 
        Author text without newlines
    abstract : str
        Abstract text without newlines
    font_name : str
        Name of the font file with extension
    font_location : str
        Directory fo the font file (with trailing slash)
    font_size : int, optional
        Font size for author and text fonts, by default 18
    title_size : int, optional
        Font size for the title, by default 20
    title_font_style : int, optional
        Title font style, as indexed in font file. Bold is often 1, but sometimes other numbers. By default 1
    author_font_style : int, optional
        Author font style, as indexed in font file. Italic is often 2, but sometimes other numbers. By default 2
    text_font_style : int, optional
        Regular text font style, as indexed in font file. By default 0
    line_spacing : int, optional
        Line spacing for text, by default 10
    image_width : int, optional
        Overall width in pixels, by default 1000
    horizontal_padding : int, optional
        Horizontal margins in pixels, by default 50
    vertical_padding : int, optional
        Vertical margins in pixels, by default 50
    section_spacing : int, optional
        Spacing between sections in pixels, by default 25
    min_height : int or None, optional
        Minimum total image height, default is None.

    Returns
    -------
    PIL.Image
    """
    title_font, author_font, abstract_font = build_fonts(
        font_name,
        font_location,
        size=font_size,
        title_size=title_size,
        title_index=title_font_style,
        author_index=author_font_style,
        regular_index=text_font_style,
    )
    tfc = [
        (text_cleanup(title), title_font, True, line_spacing),
        (text_cleanup(authors), author_font, True, line_spacing),
        (text_cleanup(abstract), abstract_font, False, line_spacing),
    ]
    return assemble_image(
        tfc,
        image_width,
        horizontal_padding,
        vertical_padding,
        section_spacing,
        min_height,
    )


def text_cleanup(text):
    text = re.sub("‐", "-", text)
    return text
