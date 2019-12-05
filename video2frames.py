import os
import cv2


def video_to_frames(vid_path, out_frame_path, start_frame=0, end_frame=None, sample_step=1):
    if not os.path.exists(vid_path):
        print('Error: no video file', vid_path)
        return

    print('decoding video %s ...'%vid_path)
    reader = cv2.VideoCapture(vid_path)
    num_frames = reader.get(cv2.CAP_PROP_FRAME_COUNT)
    if start_frame >= num_frames:
        #print('done')
        return
    start_frame = max(0, start_frame)
    reader.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    end_frame = num_frames-1 if (end_frame is None) else min(end_frame, num_frames-1)

    if not os.path.exists(out_frame_path):
        os.makedirs(out_frame_path)

    fcount = start_frame
    while fcount < end_frame:
        status, frame = reader.read()
        if not status:
            break
        if (fcount - start_frame) % sample_step == 0:
            # save frame
            cv2.imwrite(out_frame_path+'/%05d.jpg'%(fcount+1), frame)  # [int(cv2.IMWRITE_JPEG_QUALITY), 100],default 95
        fcount += 1

    reader.release()
    #print('done')


def video_to_frames_ffmpeg(vid_path, out_frame_path, quality=2):
    if not os.path.exists(vid_path):
        print('Error: no video file', vid_path)
        return

    print('decoding video %s ...' % vid_path)

    if not os.path.exists(out_frame_path):
        os.makedirs(out_frame_path)

    # ffmpeg -i input.flv -vf fps=1 out%d.png
    command = 'ffmpeg -loglevel panic -i \"{}\" -qscale:v {} \"{}/%05d.jpg\"'.format(
        vid_path, quality, out_frame_path)

    print(command)
    os.system(command)
    #sp.call(command, shell=True)


def frames_to_video(frame_path, out_vid_path, fps=30, size=None):
    if not os.path.exists(frame_path) or not os.path.isdir(frame_path):
        print('Error: %s is not a valid directory' % frame_path)
        return


    flist = [f for f in os.listdir(frame_path) if f.endswith('.jpg')]  # or other format
    if len(flist) == 0:
        print('no frame to write:', frame_path)
        return
    flist.sort()

    print('generating video %s ...' % out_vid_path)

    if not size:
        tmp_img = cv2.imread(frame_path+'/'+flist[0])
        size = (tmp_img.shape[1], tmp_img.shape[0])

    fourcc = cv2.cv.CV_FOURCC(*'MP4V')
    writer = cv2.VideoWriter(out_vid_path, fourcc, fps, size)

    for img_name in flist:
        img = cv2.imread(frame_path+'/'+img_name)
        writer.write(img)

    writer.release()

