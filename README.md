# Contract_segmentation
Python functions for to segment contracts into clauses.

## The script can process: Unstructured supported file types:
Plaintext .eml, .html, .md, .msg, .rst, .rtf, .txt, .xml Images .png, .jpg, .jpeg, .tiff, .bmp, .heic Documents .csv, .doc, .docx, .epub, .odt, .pdf, .ppt, .pptx, .tsv, .xlsx

## Usage:
The jupyter notebook included in the repo has examples how to use the python script.

Helpers:
pretty_print : Is for basic printing of the segmented clauses
full_print : Is used when the H_level columns are present in the dataframe. 
build_parent_tree: Is used to build a tree from the H_level column.

## Results:
The following image shows the results after the segmentation:

![image](https://github.com/mbenetti/contract_segmentation/assets/27162948/8ee1e7d4-87e8-4fa5-a74f-c8657388d73b)

