# Pixeldrain File Uploader and Keepalive Script

This script allows you to upload files to Pixeldrain and keep them alive by accessing them once within a specified number of days.
## Features

- **Upload Files**: Upload files to Pixeldrain and get the file link.
- **Keep Files Alive**: Access files once within a specified number of days to keep them alive.


## Requirements

- Python 3.6+
- `requests` library
- `python-dotenv` library
- `rich` library

## Installation

1. Clone the repository or download the script.
2. Install the required libraries:
    ```sh
    pip install requests python-dotenv rich
    ```
3. Create a `.env` file in the same directory as the script with the following content:
    ```env
    PIXELDRAIN_UPLOAD_URL=https://pixeldrain.com/api/file
    PIXELDRAIN_VIEW_URL=https://pixeldrain.com/u
    VISIT_INTERVAL=120
    JSON_FILE=pixeldrain_files.json
    API_KEY=your_pixeldrain_api_key
    ```

## Usage

### Upload a File

To upload a file to Pixeldrain, use the `--upload` argument followed by the file path:

```sh
python pxldrain.py --upload path/to/your/file.txt
```

### Keep Files Alive

To keep files alive by visiting them periodically, use the `--alive` argument:

```sh
python pxldrain.py --alive
```

### Help

To see the help message with all available options, use:

```sh
python pxldrain.py --help
```

## Example

### Uploading a File

```sh
python pxldrain.py --upload example.txt
```

### Keeping Files Alive

```sh
python pxldrain.py --alive
```

## TODO

- [ ] Implement progress bar for file uploads
- [ ] Improve documentation
- [ ] Optimize code for performance
- [ ] Add error handling for failed uploads and keepalive requests
- [ ] Add support for multiple file uploads and keepalive accesses
