import rawpy
import numpy as np
import cv2
import getopt
import sys, os
import exifread
from tqdm import tqdm

# Global variables
default_path = "demo"
saveInfo = False  # Whether to save the information
verbose = 1  # 1: only progress bar, 2: only txt info

# Define All options
shortOpts = "hf:iv:"
longOpts = ["help", "file=", "info", "verbose="]


def getCameraInfo(filePath: str) -> object:
    """
    Get the camera information from the image
    :param filePath [str]: The path of the raw file
    :param verbose [bool]: Whether to print the information
    :return: [object] The camera information
    """
    # Read raw image
    rawImg = open(filePath, "rb")
    rawInfo = exifread.process_file(rawImg)

    # Get the camera information
    cameraInfo = {
        "model": rawInfo["Image Model"],
        "iso": rawInfo["EXIF ISOSpeedRatings"],
        "shutter": rawInfo["EXIF ExposureTime"],
        "aperture": rawInfo["EXIF FNumber"],
        "focal": rawInfo["EXIF FocalLength"],
        "date": rawInfo["EXIF DateTimeOriginal"],
    }
    return cameraInfo


def getRawData(filePath: str) -> {np.ndarray, object}:
    """
    Restore raw data from CR2, NEF, ARW, etc. file
    :param filePath [str]: The path of the raw file
    :return: [np.ndarray] The raw data
    :return: [object] The raw data information
    """
    # Read RAW image and get CFA image data
    rawImg = rawpy.imread(filePath)
    rawData = rawImg.raw_image_visible

    # Get all the information of the image from RAW image header
    rawInfo = {
        "size": rawImg.sizes,  # Image size
        "type": rawImg.raw_type,  # RAW image type (uint8, uint16, etc.)
        "color": rawImg.color_desc,  # Color description (sRGB, AdobeRGB, etc.)
        "pattern": rawImg.raw_pattern,  # Bayer pattern (RGGB, etc.)
        "white": rawImg.white_level,  # The maximum value of the image
        "black": rawImg.black_level_per_channel,  # The minimum value of the image
        "matrix": rawImg.color_matrix,  # Color matrix
    }
    return rawData, rawInfo


def infer_bayer_pattern(raw_pattern):
    """
    Infer the Bayer pattern string from raw pattern array.

    :param raw_pattern: np.ndarray, raw pattern (e.g., [[0, 1], [3, 2]])
    :return: str, inferred Bayer pattern (e.g., 'RGGB')
    """
    # Define the possible color mappings
    color_mapping = {0: "R", 1: "G", 2: "B", 3: "G"}

    # Infer the Bayer pattern
    bayer_pattern = "".join(
        [color_mapping[pixel] for row in raw_pattern for pixel in row]
    )
    return bayer_pattern


def debayer(raw_data, color_desc, raw_pattern):
    """
    Perform debayering on raw data based on color description and pattern.

    :param raw_data: np.ndarray, raw image data
    :param color_desc: bytes, color description (e.g., b'RGBG')
    :param raw_pattern: np.ndarray, raw pattern (e.g., [[0, 1], [3, 2]])
    :return: np.ndarray, debayered image
    :raise ValueError: if color_desc does not start with b' indicating it is not a Bayer pattern
    """
    # Check if the color description starts with b' indicating Bayer pattern
    if not isinstance(color_desc, bytes):
        raise ValueError(
            f"Unsupported color description: {color_desc}. Must be bytes indicating Bayer pattern."
        )

    # Infer the Bayer pattern from raw pattern
    bayer_pattern = infer_bayer_pattern(raw_pattern)

    # Define a dictionary to map inferred Bayer pattern to OpenCV conversion codes
    color_conversion_dict = {
        "RGGB": cv2.COLOR_BAYER_RG2RGB,
        "BGGR": cv2.COLOR_BAYER_BG2RGB,
        "GRBG": cv2.COLOR_BAYER_GR2RGB,
        "GBRG": cv2.COLOR_BAYER_GB2RGB,
    }

    # Check if the inferred Bayer pattern is supported
    if bayer_pattern not in color_conversion_dict:
        raise ValueError(f"Unsupported Bayer pattern: {bayer_pattern}")

    # Get the OpenCV conversion code
    conversion_code = color_conversion_dict[bayer_pattern]

    # Perform the debayering
    debayered_image = cv2.cvtColor(raw_data, conversion_code)

    return debayered_image


def _printHelp_():
    """
    Print the help information
    """
    print("Usage: python getraw.py [options] [file path]")
    print("Options:")
    print("  -h, --help\t\t\tPrint the help information")
    print("  -f, --file [file path]\tSpecify the file path or folder path")
    print("  -i, --info\t\t\tSave the information of the image")
    print(
        "  -v, --verbose [level]\tSet the verbose level (1: only txt info, 2: only progress bar, 3: both)"
    )
    print("Example:")
    print("  python getraw.py -f ./test.CR2 -i -v 3")
    print("  !!! You can also specify a folder path !!!")
    print("  python getraw.py -f ./test/ -i -v 3")


def _getOpt_():
    """
    Get the command line options
    """
    global default_path, saveInfo, verbose

    # Get all the arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortOpts, longOpts)
    except getopt.GetoptError:
        _printHelp_()
        exit(0)

    # Handle all the arguments
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            _printHelp_()
            exit(0)
        elif opt in ("-f", "--file"):
            default_path = arg
        elif opt in ("-i", "--info"):
            saveInfo = True
        elif opt in ("-v", "--verbose"):
            verbose = int(arg)

    # If no file name is given, exit
    if default_path == "":
        print("Please enter the file name!")
        exit(0)


def _printInfo_(rawInfo: object, camInfo: object):
    """
    Print the information of the image
    :param rawInfo [object]: The information of the raw image
    :param camInfo [object]: The information of the camera
    """
    print("\033[1;36mRAW image information:\033[0m")
    print("\033[1;34m- Image size:\033[0m")
    print(f"(H: {rawInfo['size'].height}, W: {rawInfo['size'].width})")
    print("\033[1;34m- RAW image type:\033[0m")
    print(rawInfo["type"])
    print("\033[1;34m- Color description:\033[0m")
    print(rawInfo["color"])
    print("\033[1;34m- CFA pattern:\033[0m")
    print(rawInfo["pattern"])
    print("\033[1;34m- White level:\033[0m")
    print(rawInfo["white"])
    print("\033[1;34m- Black level:\033[0m")
    print(rawInfo["black"])
    print("\033[1;34m- Color matrix:\033[0m")
    print(rawInfo["matrix"])
    print()
    print("\033[1;36mCamera information:\033[0m")
    print("\033[1;34m- Camera model:\033[0m")
    print(camInfo["model"])
    print("\033[1;34m- ISO:\033[0m")
    print(camInfo["iso"])
    print("\033[1;34m- Shutter speed:\033[0m")
    print(camInfo["shutter"])
    print("\033[1;34m- Aperture:\033[0m")
    print(camInfo["aperture"])
    print("\033[1;34m- Focal length:\033[0m")
    print(camInfo["focal"])
    print("\033[1;34m- Shooting date:\033[0m")
    print(camInfo["date"])
    print()


def _saveInfo_(savePath: str, rawInfo: object, camInfo: object):
    """
    Save the information of the image
    :param savePath [str]: The path to save the information
    :param rawInfo [object]: The information of the raw image
    :param camInfo [object]: The information of the camera
    """
    with open(savePath, "w") as file:
        file.write("RAW image information:\n")
        file.write(
            f"- Size: (H: {rawInfo['size'].height}, W: {rawInfo['size'].width})\n"
        )
        file.write(f"- Type: {rawInfo['type']}\n")
        file.write(f"- Color: {rawInfo['color']}\n")
        file.write(f"- Pattern: {rawInfo['pattern']}\n")
        file.write(f"- White_level: {rawInfo['white']}\n")
        file.write(f"- Black_level: {rawInfo['black']}\n")
        file.write(f"- Color_matrix: {rawInfo['matrix']}\n")
        file.write("\n")
        file.write("Camera information:\n")
        file.write(f"- Camera_model: {camInfo['model']}\n")
        file.write(f"- ISO: {camInfo['iso']}\n")
        file.write(f"- Shutter_speed: {camInfo['shutter']}\n")
        file.write(f"- Aperture: {camInfo['aperture']}\n")
        file.write(f"- Focal_length: {camInfo['focal']}\n")
        file.write(f"- Shooting_date: {camInfo['date']}\n")
        file.write("\n")


if __name__ == "__main__":
    # Introduction
    # This file is used to restore raw data from RAW image
    # RAW image could be obtained from any brand of camera
    # It would show all the information of the image in terminal
    # You can either specify a file path or a folder path

    # Get all the arguments
    _getOpt_()

    # Get the file name
    if os.path.isdir(default_path):
        files = os.listdir(default_path)  # Get all the files in the folder
    else:
        if not os.path.isfile(default_path):
            print("File not exist!")
            exit(0)
        files = [default_path]  # Get the file name
        default_path = os.path.dirname(default_path)  # Get the folder path

    # Show the progress bar
    progBar = tqdm(files, disable=verbose != 1)

    # Get the raw data and information
    for file in progBar:
        # Pass Condition
        if os.path.isdir(f"{default_path}/{file}"):
            continue  # Skip the folder
        if file.split(".")[-1] not in ["CR2", "NEF", "ARW"]:
            continue  # Skip the non-RAW image

        # Get the file name & Update the progress bar
        fileName = file.split("/")[-1].split(".")[0]
        extName = file.split("/")[-1].split(".")[-1]
        progBar.set_description(f"Processing {fileName}")

        # Get the raw data and information
        progBar.set_postfix_str("->RAW------------")
        rawData, rawInfo = getRawData(default_path + "/" + fileName + "." + extName)
        camInfo = getCameraInfo(default_path + "/" + fileName + "." + extName)

        # Save the raw data
        rawData.tofile(f"{default_path}/{fileName}.raw")

        # Save the png image
        progBar.set_postfix_str("->--->PNG-----")
        pngImg = np.array(rawData, dtype=np.uint16)
        pngImg = pngImg.reshape(rawInfo["size"].height, rawInfo["size"].width)
        pngImg = debayer(pngImg, rawInfo["color"], rawInfo["pattern"])
        cv2.imwrite(f"{default_path}/{fileName}.png", pngImg)

        # Flat and Remove \n in the matrix & pattern
        rawInfo["pattern"] = str(rawInfo["pattern"]).replace("\n", "")
        rawInfo["matrix"] = str(rawInfo["matrix"]).replace("\n", "")

        # Save the raw information
        progBar.set_postfix_str("->--->--->INFO")
        if saveInfo:
            _saveInfo_(f"{default_path}/{fileName}.txt", rawInfo, camInfo)

        # Print the information
        if verbose == 2:
            _printInfo_(rawInfo, camInfo)
