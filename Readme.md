# RAW Image Processor

## Introduction

This is a simple image processor that can turn a commercial RAW image (as `.CR2`, `.NEF`, `.ARW` etc.) into a .png file. It is written in Python and uses the `rawpy` libraries.

## Functionality

- Get the RAW data from the image and save it as a `.raw` file.

- Convert the `.raw` file into a `.png` file.

- Read the header of RAW image and save it as a `.txt` file.

## Requirements

- Python 3.10 or higher
- Libraries: `rawpy`, `numpy`, `opencv-python`, `exifread`
    (view the [requirements.txt](requirements.txt) file for more details)

## Installation

### 1. Clone the repository

```bash
git clone
```

### 2. (Optional) Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows User: `venv\Scripts\activate`
```

### 3. Install the required libraries

```bash
pip install -r requirements.txt
```

## Usage

### 1. Script and Arguments

```bash
python getraw.py -f <path_to_raw_image(or_folder)>
```

| Argument | Description |
| --- | --- |
| `-f` or `--file` | Path to the raw image file or folder containing raw images. |
| `-i` or `--info` | (Optional) Print the information of the raw image. |
| `-v` or `--verbose` | (Optional) Print the processing information. |
| `-h` or `--help` | (Optional) Show the help message. |

### 2. Verbose Mode

| Mode | Description |
| --- | --- |
| `0` | No output. |
| `1` | Show the progress bar. |
| `2` | Show the processing information. |

### 2. Output

The output files will be saved in the same directory as the raw image file. The output files include: (For example, if the raw image is `image.CR2`)

- `image.raw`: The raw data of the image.
- `image.png`: The processed image in PNG format.
- `image.txt`: The header information of the raw image.

When processing multiple raw images in a folder, the output files will be saved in the same folder as the raw images. The output files will have the same name as the raw images with the corresponding extensions.

### 3. Information in the `.txt` file

The `.txt` file contains the following information:

- RAW image information:

  - Size: `Height` and `Width` of the image.
  - Type: The type of the raw image.
  - Color: The color pattern of the raw image. (e.g., `b'RGBG'`)
  - Pattern: The color pattern of the raw image in a 2D array. (e.g., `[[0 1] [3 2]]`), corresponding to the color pattern.
  - White_level: The white level of the raw image. (the maximum value of the pixel)
  - Black_level: The black level of the raw image. (the offset value of the pixel)
  - Color_matrix: The color matrix of the raw image.
  - Camera_model: The model of the camera.

- Camera information:
  - Camera_model: The model of the camera.(e.g., `Canon EOS 6D Mark II`)
  - ISO: The ISO value of the camera.
  - Shutter_speed: The shutter speed of the camera.
  - Aperture: The aperture value of the camera.
  - Focal_length: The focal length of the camera.
  - Shooting_date: The date and time when the image was taken.

for more information, view [demo/example.txt](demo/example.txt).

## Example

> View the [demo](demo) folder for the example raw images.

### 1. To process a single raw image

```bash
python getraw.py -f image.CR2 -i
```

This will generate `image.raw`, `image.png`, and `image.txt` in the same directory as `image.CR2`.

### 2. To process multiple raw images in a folder

```bash
python getraw.py -f /raw_images -i

# Folder structure
# /raw_images
#     image1.CR2
#     image2.CR2
```

This will generate `image1.raw`, `image1.png`, `image1.txt`, `image2.raw`, `image2.png`, `image2.txt`, etc. in the `/raw_images` folder.
