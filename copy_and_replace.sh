#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <relative-path-to-destination-repo>"
    exit 1
fi

DEST_REPO_PATH=$1
FILE_LIST="./copy_and_replace.list"
ORIGIN_REPO_NAME=$(basename "$PWD")  
DEST_REPO_NAME=$(basename "$DEST_REPO_PATH")

#cp -r . "$DEST_REPO_PATH"
rsync -av --exclude='.git' . "$DEST_REPO_PATH"

while IFS= read -r file; do
    if [ -f "$DEST_REPO_PATH/$file" ]; then
        sed -i "s/$ORIGIN_REPO_NAME/$DEST_REPO_NAME/g" "$DEST_REPO_PATH/$file"
    else
        echo "File $file not found in destination repo."
    fi
done < "$FILE_LIST"

# this section should not be needed, however the original repo is not following the convention yet and "computation-example" was used in place of the repo folder name 
while IFS= read -r file; do
    if [ -f "$DEST_REPO_PATH/$file" ]; then
        sed -i "s/computation-example/$DEST_REPO_NAME/g" "$DEST_REPO_PATH/$file"
    else
        echo "File $file not found in destination repo."
    fi
done < "$FILE_LIST"
# end of section

echo "Copy and replacement completed successfully."