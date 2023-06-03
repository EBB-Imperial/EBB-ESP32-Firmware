# this function converts txt files of form:
# [0, 0, 0, 0, 0, 0, 0, 0, 227, 24, 195, 24, 227, 24, 195, 24, 195, 24, 195, 24, 227, 24, 227, 24, 227, 24, 227, 24, 227, 24, 227, 24, 195, 24, 227, 24, 227, 24, 227, 24, 227]
# to a list of bytes
def txt_to_bin_v1(input_filename, output_filename):
    with open(input_filename, 'r') as txt_file:
        # read the file and remove whitespace characters
        data_str = txt_file.read().replace(' ', '').replace('\n', '')
        # remove the brackets
        data_str = data_str[1:-1]
        # split the string into a list of strings
        data_str_list = data_str.split(',')
        # convert list of strings to list of integers
        data_int_list = [int(item) for item in data_str_list]
        # convert list of integers to bytes
        data_bytes = bytes(data_int_list)
        
    with open(output_filename, 'wb') as bin_file:
        bin_file.write(data_bytes)

# use it like this:
# txt_to_bin_v1('raw_bytes.txt', 'output.txt')


# this function converts txt files of form:
# 0x00
# 0x00
# 0xA3
# 0x18
# 0xA3
# 0x10
# 0xA3
# 0x10
# to a list of bytes
def txt_to_bin_v2(input_filename, output_filename):
    with open(input_filename, 'r') as txt_file:
        # read the file and remove whitespace characters
        data_str = txt_file.read().replace(' ', '').replace('\n', '')
        # split the string into a list of strings
        data_str_list = data_str.split('0x')
        # remove the first empty string
        data_str_list = data_str_list[1:]
        # convert list of strings to list of integers
        data_int_list = [int(item, 16) for item in data_str_list]
        # convert list of integers to bytes
        data_bytes = bytes(data_int_list)
        
    with open(output_filename, 'wb') as bin_file:
        bin_file.write(data_bytes)

# use it like this:
txt_to_bin_v2('recorded_inputs/one_image_data.txt', 'recorded_inputs\one_image_data_bytes.txt')