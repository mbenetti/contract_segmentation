# %%
# Example usage
from segmentationv2 import *

# Document to process
file_path = '01.pdf'

# Declare the locators or anchors for H1 H2 and H3
import string

H1_1 = ['SECTION', 'ARTICLE', 'DEFINITIONS']
H1_2 = ['I. ', 'II. ', 'III. ', 'IV. ', 'V. ', 'VI. ', 'VII. ', 'VIII. ', 'IX. ', 'X. ']
H1_3 = ['1.','2.','3.','4.','5.','6.','7.','8.','9.','10.','11.','12.','13.','14.','15.','16.','17.','18.','19.','20.']
H1_4 = [f"{a}{b}" for a in string.ascii_uppercase for b in string.ascii_uppercase] # Combination of two capital letters together
H1_5 = [f"{i}.{j}" for i in range(1, 20) for j in range(1, 20)] # two digits separated by a dot
H1_6 = ['A. ', 'B. ', 'C. ', 'D. ', 'E. ', 'F. ', 'G. ', 'H. ', 'I. ', 'J. ', 'K. ', 'L. ', 'M. ', 'N. ', 'O. ', 'P. ', 'Q. ', 'R. ', 'S. ', 'T. ', 'U. ', 'V. ', 'W. ', 'X. ', 'Y. ', 'Z. ']
H1s =  H1_1 + H1_2 + H1_3 + H1_4 + H1_5 + H1_6

H2s = []
H3s = []

# Base processing
df = base_processing(file_path, H1s, H2s, H3s)


#%%
# Clean if need it
df = df[~df['elements'].isin(['footer', 'page_break'])].reset_index(drop=True)
df['H_level'] = df['elements']

# Consolidation
df = build_parent_tree(df)
df = consolidate_sections(df)
df = build_parent_tree(df)
df = merge_p_with_previous_level(df)
# # df = build_parent_tree(df)

# full_print(df)
pretty_print(df)



# %%
