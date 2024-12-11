from PIL import Image
import numpy as np


def open_image(image_path):
    # Open the image using Pillow
    image = Image.open(image_path)

    # print image size
    print(image.size)

    return np.array(image)


def save_image(image_array, output_path):
    
    print(f"Saving image to {output_path}")
    
    # Create an Image object from the array
    image = Image.fromarray(image_array)
    
    print(f"Image size: {image.size}")

    # Save the image
    image.save(output_path)


def crop_and_append(image_array, N):

    # Get the dimensions of the image
    height, width, channels = image_array.shape

    # Crop the left N pixels
    left_crop = image_array[:, :N, :]

    # Get the remaining part of the image
    remaining_part = image_array[:, N:, :]

    # Concatenate the cropped part to the right of the remaining part
    result_array = np.hstack((remaining_part, left_crop))

    return result_array


def vertical_crop_with_fixed_height(image_array, window_height, height_offset):

    # Get the dimensions of the image
    height, width, channels = image_array.shape

    # Crop the top N pixels
    top_crop = image_array[height_offset : height_offset + window_height, :, :]

    return top_crop


def join(image_array_l, image_array_r):

    # Get the dimensions of the image
    height, width, channels = image_array_l.shape

    # Concatenate the left and right images
    result_array = np.vstack((image_array_l, image_array_r))

    return result_array


def process_images(
    image_array_l,
    image_array_r,
    vertical_shift,
    horizontal_shift,
    right_eye_rotation,
    window_height,
):

    if vertical_shift > 0:
        height, width, channels = image_array_l.shape
        height_offset = int(height * vertical_shift)
        if height_offset + window_height > height:
            print("Error: The vertical shift is too large")
        image_array_l = vertical_crop_with_fixed_height(
            image_array_l, window_height, height_offset
        )
        image_array_r = vertical_crop_with_fixed_height(
            image_array_r, window_height, height_offset
        )

    if horizontal_shift > 0:
        height, width, channels = image_array_l.shape
        N = int(width * horizontal_shift)
        image_array_l = crop_and_append(image_array_l, N)
        image_array_r = crop_and_append(image_array_r, N)

    if right_eye_rotation > 0:
        height, width, channels = image_array_l.shape
        N = int(width * right_eye_rotation)
        image_array_r = crop_and_append(image_array_r, N)

    return image_array_l, image_array_r


def isValid(process):
    if process == "yes":
        return True
    if process == "True":
        return True
    if process == "1":
        return True
    if process == 1:
        return True
    if process == True:
        return True
    if process == "true":
        return True
    if process == "TRUE":
        return True


if __name__ == "__main__":

    import argparse
    import pandas
    import os

    parser = argparse.ArgumentParser(description="Crop and append an image")
    parser.add_argument("--csv", help="Path to the CSV file", default="files.csv")
    parser.add_argument(
        "--input_folder",
        help="Path to the folder containing the images",
        default="./pano_pairs",
    )
    parser.add_argument(
        "--output_folder", help="Path to the output folder", default="./output"
    )
    # parser.add_argument('--input_l', help='Path to the left input image')
    # parser.add_argument('--input_r', help='Path to the right input image')
    # parser.add_argument('--output', help='Path to the output image', default='output.png')
    # parser.add_argument('--horizontal_shift', help='Ratio of horizontal shift', type=float, default=0)
    # parser.add_argument('--vertical_shift', help='Ratio of vertical shift', type=float, default=0)
    # parser.add_argument('--right_eye_rotation', help='Zero parallax point', type=float, default=0)
    # parser.add_argument('--join', help='Join the images', action='store_true')

    args = parser.parse_args()


    if args.csv:
        df = pandas.read_csv(args.csv)

        print(df)

        counter = 0
        for index, row in df.iterrows():
            if isValid(row["process"]):
                print(f"Processing row {index} with name {row['left']} and {row['right']}")
                try:
                    image_array_l = open_image(
                        os.path.join(args.input_folder, row["left"])
                    )
                    image_array_r = open_image(
                        os.path.join(args.input_folder, row["right"])
                    )

                    image_array_l, image_array_r = process_images(
                        image_array_l,
                        image_array_r,
                        row["vertical_shift"],
                        row["horizontal_shift"],
                        row["right_eye_rotation"],
                        row["window_height"],
                    )

                    # if args.join:
                    result_array = join(image_array_l, image_array_r)
                    save_image(
                        result_array, os.path.join(args.output_folder, row["output"])
                    )
                    # else:
                    # save_image(image_array_l, row['output_l'])
                    # save_image(image_array_r, row['output_r'])
                except Exception as e:
                    print(f"Error at index{index}: {e}")
                    continue
                counter += 1
            else:
                print(f"Skipping row {index} with name {row['left']} process value {row['process']}")

        print(f"Processed {counter} images")
