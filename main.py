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
    zero_point_l,
    zero_point_r,
    window_height,
    treat_as_center=False,
    cut_from_bottom=False
):

    if vertical_shift >= 0 or window_height > 0:
        height, width, channels = image_array_l.shape
        if vertical_shift < 1:
            vertical_shift = int(height * vertical_shift)
        else:
            vertical_shift = int(vertical_shift)
            
        if cut_from_bottom:
            height_offset = vertical_shift - window_height
            if height_offset < 0:
                raise ValueError("Window height + vertical offset is less than 0")
            print(f"Cutting from bottom: {vertical_shift} px")
        else:
            height_offset = vertical_shift
            if height_offset + window_height > height:
                raise ValueError("Window height + vertical offset is greater than the image height")
            print(f"Cutting from top: {height_offset} px")
            
            
        image_array_l = vertical_crop_with_fixed_height(
            image_array_l, window_height, height_offset
        )
        image_array_r = vertical_crop_with_fixed_height(
            image_array_r, window_height, height_offset
        )

    if horizontal_shift >= 0:
        height, width, channels = image_array_l.shape
        if horizontal_shift < 1:
            N = int(width * horizontal_shift)
        else:
            N = int(horizontal_shift)
        if treat_as_center:
            shift = int(width / 2) - N
            print(f"Centering around px: {N}")
        else:
            shift = N
            print(f"Starting image at px: {N}")
        image_array_l = crop_and_append(image_array_l, shift)
        image_array_r = crop_and_append(image_array_r, shift)
        
    diff = zero_point_l - zero_point_r
    if diff != 0:
        height, width, channels = image_array_l.shape
        N = int(diff)
        print(f"Right eye rotation: {N} px")
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
                        row["vertical_crop"],
                        row["horizontal_shift"],
                        row["zero_point_l"],
                        row["zero_point_r"],
                        row["window_height"],
                        treat_as_center=isValid(row["to_center"]),
                        cut_from_bottom=isValid(row["from_bottom"])
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
