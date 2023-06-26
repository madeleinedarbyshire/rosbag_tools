# To be run with nvcr.io/nvidia/pytorch:20.11-py3 docker image.
import argparse
import cv2
import logging
import re
import rosbag
import os

from cv_bridge import CvBridge
from dropbox_tools import authenticate, download_file_from_dropbox

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def write_bag_images(bridge: object, bag: object, topic: str, write_dir: str, compressed=False, sample=False):
    bagContents = bag.read_messages(topic)
    os.makedirs(write_dir, exist_ok=True)
    for _, msg, t in bagContents:
        if compressed:
            img = bridge.compressed_imgmsg_to_cv2(msg)
        else:
            img = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        cv2.imwrite(f'{write_dir}/{str(t.secs)}.{str(t.nsecs).zfill(9)}.jpg', img)
        if sample:
            break

def write_video(bridge: object, bag: object, topic: str, write_dir: str, video_name: str, compressed=True):
    bagContents = bag.read_messages(topic)
    images = []
    for _, msg, t in bagContents:
        if compressed:
            img = bridge.compressed_imgmsg_to_cv2(msg)
        else:
            img = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        height, width, _ = img.shape
        size = (width,height)
        images.append(img)

    if len(images) > 0:
        out = cv2.VideoWriter(f'{write_dir}/{video_name}.mp4',cv2.VideoWriter_fourcc(*'mp4v'), 15, size)
        for i in range(len(images)):
            out.write(images[i])
        out.release()

def write_images_from_dropbox(bridge: object, bag_dir: str, first_bag: str, topic: str, write_dir: str, compressed: bool, sample: bool):
    dbx = authenticate()
    logging.info(f'Writing images from topic {topic} to {write_dir}')
    all_bags = sorted([entry.name for entry in dbx.files_list_folder(bag_dir, limit=2000).entries])
    try:
        index = all_bags.index(first_bag)
    except:
        logging.warning(f'Cannot find: {first_bag}')

    total = 0
    for j, bag_file in enumerate(all_bags[index:]):
        bag_number = int(re.search('_(.*?)\.', bag_file).group(1))
        if bag_number == 0 and j != 0:
            break
        else:
            download_file_from_dropbox(dbx, os.path.join(bag_dir, bag_file), f'./{bag_file}')
            bag = rosbag.Bag(f'./{bag_file}')
            write_bag_images(bridge, bag, topic, write_dir, compressed, sample)
            os.remove(f'./{bag_file}')

def write_images_from_local_storage(bridge: object, bag_dir: str, first_bag: str, topic: str, write_dir: str, compressed: bool, sample: bool):
    logging.info(f'Writing images from topic {topic} to {write_dir}')
    all_bags = sorted(os.listdir(bag_dir))
    try:
        index = all_bags.index(first_bag)
    except:
        logging.warning(f'Cannot find: {first_bag}')

    total = 0
    for j, bag_file in enumerate(all_bags[index:]):
        bag_number = int(re.search('_(.*?)\.', bag_file).group(1))
        if bag_number == 0 and j != 0:
            break
        else:
            bag = rosbag.Bag(os.path.join(bag_dir, bag_file))
            write_bag_images(bridge, bag, topic, write_dir, compressed, sample)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Write images and videos from rosbags')
    parser.add_argument('--bag-dir', default='/070623', type=str, help='Directory containing rosbags')
    parser.add_argument('--bag-file', default='2023-06-07-14-44-35_0.bag', type=str, help='First rosbag file')
    parser.add_argument('--topic', default='/back/color/image_raw', type=str, help='Rostopic to read images from')
    parser.add_argument('--write-dir', default='images', type=str, help='Folder to write images to')
    parser.add_argument('--log-file', default='out.log', type=str, help='Log file path')
    parser.add_argument('--dropbox', default=False, type=str2bool, help='Retrieve bags from dropbox')
    parser.add_argument('--compressed', default=False, type=str2bool, help='Rostopic contains compressed compressed images')
    parser.add_argument('--video', default=False, type=str2bool, help='Write images to mp4 video')
    parser.add_argument('--sample', default=False, type=str2bool, help='Sample one image from each bag')

    args = parser.parse_args()
    logging.basicConfig(filename=args.log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    bridge = CvBridge()
    first_bag_name = re.search('(.*?)_', args.bag_file).group(1)
    images_dir = os.path.join(args.write_dir, first_bag_name)

    if args.dropbox:
        write_images_from_dropbox(bridge, args.bag_dir, args.bag_file, args.topic, images_dir, args.compressed, args.sample)
    else:
        if args.video:
            write_video(bridge, args.bag_dir, args.bag_file, args.topic, args.write_dir, first_bag_name, args.compressed)
        else:
            write_images_from_local_storage(bridge, args.bag_dir, args.bag_file, args.topic, images_dir, args.compressed, args.sample)