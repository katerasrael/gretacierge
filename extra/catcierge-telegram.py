#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
from wand.image import Image
from wand.font import Font
from wand.drawing import Drawing
from wand.color import Color
import json
import os
import requests

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


kernel_size = 20
args = None

DEBUG = True

def log(s):
    if DEBUG:
        print s

def telegram_sendpic(telegram_file,bot_token,bot_chat_id):
        bot = telegram.Bot(token=bot_token)
        bot.send_photo(bot_chat_id, open(telegram_file,'rb'))

def create_kernel(w=3, h=3):
    k = Image(width=w * kernel_size + 2, height=h * kernel_size + 2)

    draw = Drawing()
    draw.fill_color = Color("white")
    draw.stroke_color = Color("black")

    for y in xrange(0,h):
        for x in xrange(0,w):
            draw.rectangle(left=x*kernel_size, top=y*kernel_size,
                            width=kernel_size, height=kernel_size)
            draw(k)

    return k

def create_row(imgs, offsets, gap, fixed_width=0, caption=None, caption_offset=(0,0)):
    row_width = 0
    i = 0
    row_height = 0

    for img in imgs:
        if isinstance(img, Image):
            row_width += img.width + gap
            row_height = max(img.height, row_height)
        else:
            row_width += offsets[i][0] + gap
        i += 1

    if fixed_width:
        row_width = fixed_width

    row = Image(width=row_width, height=row_height)

    i = 0
    x = 0

    for img in imgs:
        if isinstance(img, Image):
            row.composite(img, left=x + offsets[i], top=(row_height - img.height) / 2)
            x += img.width + offsets[i] + gap
        else:
            (offset_x, offset_y, width, font) = offsets[i]
            row.caption(img, left=x + offset_x, top=offset_y, width=250, height=250, font=font)
            x += width + gap
        i += 1

    if caption:
        caption_font = Font(path="%s/source-code-pro/SourceCodePro-Medium.otf" % args.fonts, size=14)
        row_w_caption = Image(width=row_width, height=row_height+20)
        row_w_caption.caption(caption, left=caption_offset[0], top=caption_offset[1],
                                width=1450, height=50, font=caption_font)
        row_w_caption.composite(row, left=0, top=20)
        return row_w_caption
    else:
        return row



def compose_img(img_paths=None, match_json=None, gap=5, horizontal_gap=5, description=None, caption="Catcierge", state="undefined", direction="undefined"):

    if state == "Lockout":
        background_color =  "#ff0000"   #red
    elif state == "Keep open":
        background_color =  "#ADFF2F"   #green
    else:
        background_color =  "#8A968E"   #original grey

    img = Image(width=600, height=1124, background=Color(background_color))
        
    #print("Font path: %s" % args.fonts)

    font = Font(path="%s/source-code-pro/SourceCodePro-Medium.otf" % args.fonts, size=64)
    font_title = Font(path="%s/alex-brush/AlexBrush-Regular.ttf" % args.fonts, size=64)
#    font_title = font
    font_math = Font(path="%s/Asana-Math/Asana-Math.otf" % args.fonts, size=64)


    imgs = []
    assert (img_paths and (len(img_paths) > 0)) or match_json, \
        "Missing either a list of input image paths or a match json"

    if not img_paths or len(img_paths) == 0:
        step_count = match_json["step_count"]

        for step in match_json["steps"][:step_count]:
            print("Step: %s" % step["name"])
            img_paths.append(step["path"])

    # TODO: Allow any matcher type and number of images...    

    for img_path in img_paths:
        #print img_path
        imgs.append(Image(filename=img_path))

    mpos = lambda w: (img.width - w) / 2
    x_start = 20

    # first we show the "Match %d"
    text_width = font_title.size * int((len(caption)) * 0.7)   # get width - TODO why 0.7?
    img.caption(caption, left=(img.width - text_width) / 2, top=5, width=text_width, height=100, font=font_title)
#    img.caption(caption, left=(img.width - text_width) / 2, top=5, width=text_width, height=100, font=font_title)

    # the we show the direction and description
    # TODO 
    if description:
        desc_font = Font(path="%s/source-code-pro/SourceCodePro-Medium.otf" % args.fonts, size=24)
        font_width = int(desc_font.size * 0.7)

        text_t = direction + ' - ' + description # add some information about direction
        if len(text_t) > 33:
            text = text_t[:33] + (text_t[:33] and '..') # https://stackoverflow.com/questions/2872512/python-truncate-a-long-string#
        else:
            text = text_t
            
        text_width = font_width * len(text)
        img.caption(text, left=((img.width - text_width) / 2), top=80, width=text_width, height=100, font=desc_font)
        height = 120

    # show original image
    if len(img_paths) >= 1:
        orgimg = imgs[0]    # Original image.
        img.composite(orgimg, left=mpos(orgimg.width), top=height) 
    
#    kernel5x1 = create_kernel(w=5, h=1) - won't need that

    # TODO: simplify the code below by making the symbols into images before they're used to create the rows.
    if len(img_paths) >= 3:
        detected = imgs[1]    # Detected cat head roi. 
        croproi = imgs[2]    # Cropped/extended roi.
        height += orgimg.height + gap
        
        # Detected head + cropped region of interest.
        head_row = create_row([detected, croproi], [0, 0], horizontal_gap, caption="Detected head  Cropped ROI")
        img.composite(head_row, left=mpos(head_row.width), top=height)
    
    if len(img_paths) >= 6:
        globalthr = imgs[3]    # Global threshold (inverted).
        adpthr = imgs[4]    # Adaptive threshold (inverted).
        combthr = imgs[5]    # Combined threshold.

        height += head_row.height + gap
        # Combine the threshold images.
        thr_row = create_row([globalthr, "+", adpthr, "=", combthr],
                            [x_start,
                            (4 * horizontal_gap, -15, 14 * horizontal_gap, font),
                            0,
                            (2 * horizontal_gap, -15, 8 * horizontal_gap, font),
                            2 * horizontal_gap],
                            horizontal_gap, fixed_width=img.width,
                            caption="Global Threshold           Adaptive Threshold       Combined Threshold",
                            caption_offset=(x_start, 0))
        img.composite(thr_row, left=mpos(thr_row.width), top=height)

    if len(img_paths) >= 7:
        opened = imgs[6]    # Opened image.
    
        height += thr_row.height + gap
        kernel2x2 = create_kernel(w=2, h=2)

        # Open the combined threshold.
        # utf-8 Overlay u'∘'    0x20D8
        open_row = create_row([combthr, u'\u20D8', kernel2x2, "=", opened],
                            [x_start,
                            (5 * horizontal_gap, -5, 14 * horizontal_gap, font_math),
                            0,
                            (21 * horizontal_gap, -15, 10 * horizontal_gap, font),
                            19 * horizontal_gap + 3],
                            horizontal_gap, fixed_width=img.width,
                            caption="Combined Threshold         2x2 Kernel               Opened Image",
                            caption_offset=(x_start, 0))
        img.composite(open_row, left=mpos(open_row.width), top=height)

    if len(img_paths) >= 8:
        dilated = imgs[7]    # Dilated image.

        height += open_row.height + gap
        kernel3x3 = create_kernel(w=3, h=3)

        # Dilate opened and combined threshold with a kernel3x3.
        # utf  plus in a circle    u'⊕'        0x2295
        dilated_row = create_row([opened, u'\u2295', kernel3x3, "=", dilated],
                            [x_start,
                            (3 * horizontal_gap, -5, 14 * horizontal_gap, font_math),
                            0,
                            (17 * horizontal_gap, -15, 10 * horizontal_gap, font),
                            15 * horizontal_gap + 3],
                            horizontal_gap, fixed_width=img.width,
                            caption="Opened Image               3x3 Kernel               Dilated Image",
                            caption_offset=(x_start, 0))
        img.composite(dilated_row, left=mpos(dilated_row.width), top=height)

    if len(img_paths) >= 10:
        combined = imgs[8]    # Combined image (re-inverted).
        contours = imgs[9]    # Contours of white areas.

        height += dilated_row.height + gap

        # Inverted image and contour.
        contour_row = create_row([combined, contours], [0, 0], horizontal_gap, caption="  Re-Inverted         Contours")
        img.composite(contour_row, left=mpos(contour_row.width), top=height)

    if len(img_paths) >= 11:        
        final = imgs[10]    # Final image.
        height += contour_row.height + 2 * gap

        # Final.
        img.composite(final, left=mpos(final.width), top=height)
        height += final.height + gap

    return img

def create_matches(catcierge_json, output_file, args):

    match_count = catcierge_json["match_group_count"]
    match_imgs = []
    total_width = 0
    total_height = 0
    i = 1

    # All paths in the json are relative to this.
    base_path = os.path.dirname(args.json)

    for match in catcierge_json["matches"][:match_count]:

        step_count = match["step_count"]
        img_paths = []
        log("Stepcount %d" % step_count)
        
        for step in match["steps"][:step_count]:
            img_paths.append(os.path.join(base_path, step["path"]))
            log(" %s" % step["path"])


        img = compose_img(img_paths=img_paths,
                gap=5,
                description=match["description"],
                caption="Match %d" % i, state=catcierge_json["state"], direction=match["direction"])

        total_width += img.width
        total_height = max(total_height, img.height)
        match_imgs.append(img)
        i += 1

    fimg = Image(width=total_width, height=total_height)

    x = 0
    for img in match_imgs:
        fimg.composite(img, left=x, top=0)
        x += img.width

    return fimg


def main():
    global args
    parser = argparse.ArgumentParser()

    parser.add_argument("--bot_token", metavar = "BOT_TOKEN", 
                    help = "The Token for the bot communication")

    parser.add_argument("--bot_chat_id", metavar = "BOT_CHAT_ID",
                    help = "The Telegram Chat-ID")

    parser.add_argument("--images", metavar="IMAGES", nargs="+",
                    help="The Catcierge match images to use if no json file is specified.")

    # Add support for inputting a json with the paths and stuff.
    parser.add_argument("--json", metavar="JSON",
                    help="JSON containing image paths and descriptions.")

    parser.add_argument("--output", metavar="OUTPUT",
                    help="The output file that the resulting image should be written to.")

    parser.add_argument("--fonts", metavar="FONT_DIRECTORY", default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts/"),
                    help="Path to where the fonts can be found.")

    parser.add_argument("--steps", action="store_true",
                    help="Incude the steps images.")
    # TODO: Implement NOT including steps...

    args = parser.parse_args()

    if not args.output:
        print("You must specify an output file using --output")
        return -1

    if args.images:
        image_count = len(args.images)

        try:
            img = compose_adaptive_prey(img_paths=args.images, gap=5)
            img.save(filename=args.output)
        except Exception as ex:
            print("Failed to compose images: %s" % ex.message)
    elif args.json:
        catcierge_json = json.loads(open(args.json).read())
        img = create_matches(catcierge_json, args.output, args)
        img.save(filename=args.output)
        
        if args.bot_token:
            telegram_sendpic(args.output,args.bot_token,args.bot_chat_id)

    print("Saved composed image: %s" % args.output)


if __name__ == '__main__': sys.exit(main())
