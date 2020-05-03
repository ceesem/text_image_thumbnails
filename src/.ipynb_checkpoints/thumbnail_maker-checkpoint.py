import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

font_dirs = {'global': os.path.expanduser('/Library/Fonts/'),
             'user': os.path.expanduser('~/Library/Fonts/'),
             'system': '/System/Library/Fonts/'}

def get_fonts(font_name, font_location, size=18, title_size=20, title_index=1, author_index=2, regular_index=0):
    font_loc = f"{font_location}{font_name}"
    fnt_title = ImageFont.truetype(font_loc, size=title_size, index=title_index)
    fnt_author = ImageFont.truetype(font_loc, size=size, index=author_index)
    fnt_text = ImageFont.truetype(font_loc, size=size, index=regular_index )
    return fnt_title, fnt_author, fnt_text

def join_words(line):
    return ' '.join(line)

def split_lines(txt, fnt, width, padding):
    w = width - 2 * padding

    split_text = txt.split(' ')
    lines = []
    new_line = []
    for word in split_text:
        try_new_line = fnt.getsize(join_words(new_line + [word] + [' ']))
        if try_new_line[0] <= w:
            new_line.append(word)
        else:
            lines.append(join_words(new_line) + '\n')
            new_line = [word]
    lines.append(join_words(new_line))
    return lines

def centered_box_corner(lines, fnt, width):
    bbox_width = fnt.getsize_multiline(join_words(lines))[0]
    right_corner = width / 2 - bbox_width/2
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

def assemble_image(text_font_ctr_spacing, width, w_padding, v_padding, section_spacing):
    lines_each = []
    fnts_each = []
    x_pts = []
    centered_each = []
    spacing_each = []
    for text, fnt, is_centered, spacing in text_font_ctr_spacing:
        lines = split_lines(text, fnt, width, w_padding)
        lines_each.append(''.join(lines))
        fnts_each.append(fnt)
        centered_each.append(is_centered)
        if is_centered:
            w_corner = centered_box_corner(lines, fnt, width)
        else:
            w_corner = w_padding
        x_pts.append(w_corner)
        spacing_each.append(spacing)
    
    text_fonts = [(l, f, s) for l, f, s in zip(lines_each, fnts_each, spacing_each)]
    h_all, h_each = image_height(text_fonts,
                                 v_padding,
                                 section_spacing,
                                 )
    
    img = Image.new('RGB', size=(width, h_all), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    align_lookup = {True: 'center', False:'left'}
    for line, fnt, is_centered, spacing, x, y in zip(lines_each, fnts_each, centered_each, spacing_each, x_pts, h_each):
        d.multiline_text((x,y), ''.join(line), font=fnt, align=align_lookup[is_centered], fill=(0,0,0), spacing=spacing)
    return img

def thumbnail_image(title,
                    authors,
                    abstract,
                    title_font,
                    author_font,
                    abstract_font,
                    line_spacing=10,
                    image_width=1000,
                    horizontal_padding = 50,
                    vertical_padding = 50,
                    section_spacing=25):
    
    tfc = [(title, title_font, True, line_spacing),
           (authors, author_font, True, line_spacing),
           (abstract, abstract_font, False, line_spacing)]
    return assemble_image(tfc, image_width, horizontal_padding, vertical_padding, section_spacing)