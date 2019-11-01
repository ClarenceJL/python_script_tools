# -*- coding:utf-8 -*-
# author: EverythingBagel
# date: 2019/10
from __future__ import print_function
from multiprocessing import Pool
from PIL import Image
import os
import argparse


def parse_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mode',
        default='single',
        type=str,
        help='If mode==single, combine images in src_path to a single pdf dest_path,\n'
             'Else, search every possible image directory under src_path and generate pdfs recursively.'
    )
    parser.add_argument(
        '--src_path',
        default='',
        type=str,
        help='Source directory: root path for nested image folders')
    parser.add_argument(
        '--dest_path',
        default='',
        type=str,
        help='Destination directory: root path for generated PDFs'
    )
    parser.add_argument(
        '--output_resolution',
        default=100,
        type=int,
        help='PDF resolution'
    )
    parser.add_argument(
        '--fix_image_size',
        default=-1,
        nargs='+',
        type=int
    )
    parser.add_argument(
        '--max_depth',
        default=None,
        type=int,
        help='Maximal recursion depth'
    )
    parser.add_argument(
        '--num_threads',
        default=8,
        type=int,
        help='Number of threads used'
    )

    return parser.parse_args()


def is_image(f):
    return f.endswith('.jpg') or f.endswith('.png') or f.endswith('.jpeg') or \
           f.endswith('.JPG') or f.endswith('.PNG') or f.endswith('.JPEG')


def combine_imgs_to_pdf(imgs_path, output_path, resolution=100, img_size=None):
    fname = [f for f in os.listdir(imgs_path) if is_image(f)]
    if len(fname) == 0:
        return

    # todo: filter illegal images
    
    # sort image by name
    fid = [int(''.join(c for c in s if c.isdigit())) for s in fname]
    forder = sorted(range(len(fid)), key=lambda k: fid[k])
    fname = [fname[i] for i in forder]

    # attach images to pdf file
    # todo: resize image if required

    pdf = Image.open(imgs_path+'/'+fname[0])
    if pdf.mode == "RGBA":
        pdf = pdf.convert("RGB")

    fname.pop(0)

    im_list = []
    for fpath in fname:
        img = Image.open(imgs_path+'/'+fpath)
        # todo: resize image if required

        if img.mode == "RGBA":
            img = img.convert('RGB')
            im_list.append(img)
        else:
            im_list.append(img)

    p, _ = os.path.split(output_path)
    if not os.path.exists(p):
        os.makedirs(p)

    pdf.save(output_path, "PDF", resolution=resolution, save_all=True, append_images=im_list)

    print("PDF file generated:", output_path)


def add_process(root_path, out_path, ps, depth, resolution):
    if depth is not None and depth <= 0:
        return

    assert os.path.exists(root_path), '%s is not a valid path' % root_path
    subs = os.listdir(root_path)
    for f in subs:
        if is_image(f):  # merge current path to a .pdf
            pdf_path = out_path
            if not (pdf_path.endswith('.pdf') or pdf_path.endswith('.PDF')):
                pdf_path += '.pdf'
            ps.apply_async(combine_imgs_to_pdf, args=(root_path, pdf_path, resolution, ))
            break
    else:
        for f in subs:
            if os.path.isdir(root_path + '/' + f):
                next_depth = depth - 1 if depth is not None else None
                add_process(root_path + '/' + f, out_path + '/' + f, ps, next_depth, resolution)


def batch_process(root_path, out_path, num_threads, max_depth, resolution):
    ps = Pool(num_threads)
    add_process(root_path, out_path, ps, max_depth, resolution)
    ps.close()
    ps.join()


if __name__ == '__main__':
    opts = parse_opts()

    if opts.src_path == '':
        opts.src_path = input('Please input source directory: ')
    print('Source path:', opts.src_path)

    if opts.dest_path == '':
        opts.dest_path = input('Please input destination directory: ')
    print('Destination path:', opts.dest_path)

    if opts.mode == 'single':
        # test one
        if not (opts.dest_path.endswith('.pdf') or opts.dest_path.endswith('.PDF')):
            opts.dest_path += '.pdf'
        combine_imgs_to_pdf(opts.src_path, opts.dest_path, opts.output_resolution)
    else:
        # test whole directory
        batch_process(opts.src_path, opts.dest_path, opts.num_threads, opts.max_depth, opts.output_resolution)
