# ROSbag Tools

A little library to process rosbags.

Rationale: I ran out of space to store my ROSbags locally so I started using Dropbox. This tool enables you to seamlessly process rosbag data stored locally or in Dropbox.

## Installation
Install the following packages:
```
conda install -c conda-forge ros-rospy ros-sensor-msgs ros-rosbag
pip install cvbridge3 docker
```

If you are using dropbox set up an app here: https://www.dropbox.com/developers

## Write Out Images from ROSbags
I recorded my rosbag data using `rosbag record --split --size 1024` so multiple rosbags would be created in a given round of recording. By default, these bags are timestamped and an index at the end. Given the name of the first bag and a directory, this tools will retrieve all subsequent bags and write them out to a file.
```
dir/
  |-2023-01-01-00-00-00_0.bag
  |-2023-01-01-00-00-05_1.bag
  |-2023-01-01-00-00-10_2.bag
```

To write out images from bags stored in dropbox:
```
python src/images.py --docker True --bag-dir /bags --bag-file 2023-01-01-00-00-00_0.bag --topic /back/color/image_raw/compressed --write-dir images
```

To write out images from bags stored locally:
```
python src/images.py --bag-dir bags --bag-file 2023-01-01-00-00-00_0.bag --topic /back/color/image_raw/compressed --write-dir images
```
