import pandas as pd
import re
import pandas as pd
from collections import Counter
from unstructured.partition.auto import partition
from unstructured.cleaners.core import clean
from unstructured.cleaners.core import clean_non_ascii_chars
from unstructured.cleaners.core import group_broken_paragraphs
import pandas as pd

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """
    Returns the number of tokens in a text string.

    Args:
        string (str): The input text string.
        encoding_name (str): The name of the encoding to use.

    Returns:
        int: The number of tokens in the input string ('text' column).
        
    Usage to add a new column with the count:
        df['num_tokens'] = df['text'].apply(lambda x: num_tokens_from_string(x, "cl100k_base"))
    """
    import tiktoken
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
    
def process_file(file_name):
    """
    This function takes a file name as input, processes the file using the unstructured library,
    and returns a pandas DataFrame with the cleaned text.
    """    
    # Partition the file into elements using the unstructured library
    elements = partition(file_name, strategy="fast")
    
    # Convert the elements to a list of strings
    paragraphs = [str(el) for el in elements]
    
    # Create a pandas DataFrame from the list of paragraphs
    df_from_text = pd.DataFrame(paragraphs, columns=['text'])
    
    # Clean the text by removing extra whitespace and bullets
    df_from_text['text'] = df_from_text['text'].apply(clean, extra_whitespace=True, bullets=True)
    
    # Clean non-ASCII characters from the text
    df_from_text['text'] = df_from_text['text'].apply(clean_non_ascii_chars)
    
    # Group broken paragraphs together
    df_from_text['text'] = df_from_text['text'].apply(group_broken_paragraphs)
    
    return df_from_text

def extract_first_word(df):
    # Apply a lambda function to the 'text' column
    # Split the text into a list of words
    # Take the first word from the list
    # Join the word back into a string
    df['first_word'] = df['text'].apply(lambda x: ' '.join(x.split()[:1]))
    return df

def extract_first_character(df):
    # Apply a lambda function to the 'text' column
    # Take the first character from the text
    df['first_character'] = df['text'].apply(lambda x: x[0] if x else '')
    return df

def extract_first_two_words(df):
    # Apply a lambda function to the 'text' column
    # Split the text into a list of words
    # Take the first two words from the list
    # Join the two words with a space
    # Assign the result to a new column 'first_two_words'
    df['first_two_words'] = df['text'].apply(lambda x: ' '.join(x.split()[:2]))
    return df

def extract_first_two_characters(df):
    # Apply a lambda function to the 'text' column
    # Take the first two characters from the text
    df['first_two_characters'] = df['text'].apply(lambda x: x[:2] if x else '')
    return df

def extract_first_three_words(df):
    # Apply a lambda function to the 'text' column
    # Split the text into a list of words
    # Take the first three words from the list
    # Join the words back into a string
    df['first_three_words'] = df['text'].apply(lambda x: ' '.join(x.split()[:3]))
    return df

def add_elements_column(df):
    # Initialize an empty list to store elements
    import re
    elements = []
    
    # Iterate over the 'first_two_words' column of the DataFrame
    for text in df['first_two_words']:
        # Use regular expression to search for 'Page' followed by digits
        page_indicator = re.search(r'Page\s*(\d+)', text)
        
        # If a page indicator is found, set the element to 'page_break'
        if page_indicator:
            element = "page_break"
        # Otherwise, set the element to None
        else:
            element = None
        
        # Append the element to the list
        elements.append(element)
    
    # Add a new column 'elements' to the DataFrame with the list of elements
    df['elements'] = elements
    
    # Return the updated DataFrame
    return df

def update_elements(df, H1s, H2s, H3s):
    # Iterate over each row in the DataFrame
    import string  # Import string module (already imported at the top)
    for i, row in df.iterrows():
        text = row['first_two_words']
        # Check if the first word matches any H3 element
        for h3 in H3s:
            if h3 in text:
                df.at[i, 'elements'] = 'H3'  # Set the 'elements' column to 'H3'
                break  # Exit the H3 loop since a match was found
        # If not H3, check if the first word matches any H2 element
        else:
            for h2 in H2s:
                if h2 in text:
                    df.at[i, 'elements'] = 'H2'  # Set the 'elements' column to 'H2'
                    break  # Exit the H2 loop since a match was found
            # If not H2, check if the first word matches any H1 element
            else:
                for h1 in H1s:
                    if h1 in text:
                        df.at[i, 'elements'] = 'H1'  # Set the 'elements' column to 'H1'
                        break  # Exit the H1 loop since a match was found

    # Return the updated DataFrame
    return df  # Return the modified DataFrame

def change_first_row(df):
    # Assign the 0 to the original section
    # Check if the minimum index value is 0
    if df.index.min() == 0:
        # If true, assign 'H0' to the 'elements' column at index 0
        df.loc[0, 'elements'] = 'H0'
    else:
        # If false, assign 'H0' to the 'elements' column at the minimum index value
        df.loc[df.index.min(), 'elements'] = 'H0'
        
    # Return the modified DataFrame
    return df

def promote_h2(df):
    # Define a function to check if a string is all uppercase
    def is_all_caps(text):
        return all(char.isupper() for char in text if char.isalpha())
    
    # For rows where the 'elements' column is 'H2', check if the first three words are all uppercase
    # If so, change the 'elements' value to 'H1', otherwise leave it as 'H2'
    df.loc[df['elements'] == 'H2', 'elements'] = df[df['elements'] == 'H2'].apply(lambda row: 'H1' if is_all_caps(row['first_three_words']) else row['elements'], axis=1)
    return df

def fill_empty_elements(df):
    # Replace NaN values in 'elements' column with 'p'
    df['elements'] = df['elements'].fillna('p')
    # Return the modified DataFrame
    return df

def flag_footer(df):
    # Convert the 'text' column to a list
    texts = df['text'].tolist()
    
    # Count the occurrences of each text string
    text_counter = Counter(texts)
    
    # Get the most common string and its count
    most_common_string, count = max(text_counter.items(), key=lambda x: x[1])
    
    # If the most common string appears more than once, flag it as 'footer'
    if count > 1:
        df.loc[df['text'] == most_common_string, 'elements'] = 'footer'
    
    # Return the updated DataFrame
    return df

def build_parent_tree(df):
    """
    This function builds a parent tree for H1 and H2 headers in a given DataFrame.
    It tracks the latest H1 and H2 headers and assigns them as parents to subsequent rows.
    The parent information is added as new columns to the DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame containing the 'H_level' and 'text' columns.

    Returns:
        pandas.DataFrame: The updated DataFrame with 'H1_parent' and 'H2_parent' columns.
    """
    # Initialize lists to store parent information
    H1_parent = []
    latest_h1 = None
    latest_h1_position = None
    text_content = None

    H2_parent = []
    latest_h2 = None
    latest_h2_position = None

    for i in range(len(df)):
        # Check if the current row is an H1 header
        if df.loc[i, 'H_level'] == 'H1':
            latest_h1 = df.loc[i, 'H_level']
            latest_h1_position = i
            text_content = df.loc[i, 'text']
            if text_content is not None:
                sentences = text_content.split('.')[:2]
                first_two_sentences = '.'.join(sentences) + '.'
                H1_parent.append([latest_h1_position, latest_h1, (first_two_sentences.split('\n')[0]).upper()])
            else:
                H1_parent.append([latest_h1_position, latest_h1, None])
        else:
            # Append the latest H1 information for non-H1 rows
            if text_content is not None:
                sentences = text_content.split('.')[:2]
                first_two_sentences = '.'.join(sentences) + '.'
                H1_parent.append([latest_h1_position, latest_h1, (first_two_sentences.split('\n')[0]).upper()])
            else:
                H1_parent.append([latest_h1_position, latest_h1, None])

        # Check if the current row is an H2 header
        if df.loc[i, 'H_level'] == 'H2':
            latest_h2 = df.loc[i, 'H_level']
            latest_h2_position = i
            H2_parent.append([latest_h2_position, latest_h2])
        else:
            # Append the latest H2 information for non-H2 rows
            H2_parent.append([latest_h2_position, latest_h2])

    # Reset the parent information for rows where the index matches the position
    for i in range(len(H1_parent)):
        if H1_parent[i][0] == i:
            H1_parent[i] = [None, None, None]
            H2_parent[i] = [None, None]
        if H2_parent[i][0] == i:
            H2_parent[i] = [None, None]

    # Add the parent information to the DataFrame
    df['H1_parent'] = H1_parent
    df['H2_parent'] = H2_parent

    # Reset the H2_parent for paragraphs following an H1 header
    df.loc[(df['H_level'] == 'p') & (df['H_level'].shift(1) == 'H1'), 'H2_parent'] = None

    # Number of tokens
    df['num_tokens'] = df['text'].apply(lambda x: num_tokens_from_string(x, "cl100k_base"))
    
    # Return the updated DataFrame with the same columns
    return df

def consolidate_sections(df):
    """
    Consolidates the text in a DataFrame based on the section level (H1, H2 or p).
    
    Args:
        df (pandas.DataFrame): The input DataFrame containing the 'text', 'H_level', and 'num_tokens' columns.
        
    Returns:
        pandas.DataFrame: A new DataFrame with consolidated text for each section level.
    """
    import pandas as pd
    # Initialize an empty list to store the consolidated text
    consolidated_text = []

    # Initialize variables to keep track of the current section and text
    current_section = None
    current_text = ""
    current_tokens = 0

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        text = row['text']
        section = row['H_level']  # Assuming the column name is 'H_level'
        num_tokens = row['num_tokens']
        
        # Check if the section has changed or if the number of tokens exceeds 500
        if section != current_section or (current_tokens + num_tokens) >= 150:
            # If there is text in the current section, append it to the consolidated_text list
            if current_text:
                consolidated_text.append((current_section, current_text))
            # Update the current section and reset the current text and tokens
            current_section = section
            current_text = text
            current_tokens = num_tokens
        else:
            # Append the text to the current section
            current_text += "\n" + text
            current_tokens += num_tokens

    # Append the last section if there is any remaining text
    if current_text:
        consolidated_text.append((current_section, current_text))

    # Create a new DataFrame with the consolidated text
    df_consolidated = pd.DataFrame(consolidated_text, columns=['H_level', 'text'])

    # Number of tokens
    df_consolidated['num_tokens'] = df_consolidated['text'].apply(lambda x: num_tokens_from_string(x, "cl100k_base"))
    
    return df_consolidated

def merge_p_with_previous_level(df):
    """
    Merge consecutive rows with 'p' level into a single row. Then 
    merge with previous H level
    
    Args:
        df (pandas.DataFrame): DataFrame containing 'H_level', 'text', and 'H1_parent' columns.
        
    Returns:
        pandas.DataFrame: DataFrame with merged rows.
    """
    import pandas as pd
    concatenated_text = []
    current_text = ''
    current_h_level = None
    current_h1_parent = None
    
    for index, row in df.iterrows():
        # If the current row is not a 'p' level
        if row['H_level'] != 'p':
            # Append the current text to the list if it exists
            if current_text:
                concatenated_text.append((current_text, current_h_level, current_h1_parent))
            # Start a new text with the current row
            current_text = row['text']
            current_h_level = row['H_level']
            current_h1_parent = row['H1_parent']
        else:
            # Append the current row's text to the current text
            current_text += '\n' + row['text']
    
    # Append the last text if it exists
    if current_text:
        concatenated_text.append((current_text, current_h_level, current_h1_parent))
    
    # Create a new DataFrame with the merged text
    merged_df = pd.DataFrame(concatenated_text, columns=['text', 'H_level', 'H1_parent'])
    
    # Number of tokens
    merged_df['num_tokens'] = merged_df['text'].apply(lambda x: num_tokens_from_string(x, "cl100k_base"))
    
    return merged_df

def base_processing(file_path, H1s, H2s, H3s):
    # Preparation stage
    df_from_text = process_file(file_path)
    df_from_text = extract_first_character(df_from_text)
    df_from_text = extract_first_two_characters(df_from_text)
    df_from_text = extract_first_word(df_from_text)
    df_from_text = extract_first_two_words(df_from_text)
    df_from_text = extract_first_three_words(df_from_text)
    df_from_text = add_elements_column(df_from_text)
    df_from_text = update_elements(df_from_text, H1s, H2s, H3s)
    df_from_text = change_first_row(df_from_text)
    df_from_text = flag_footer(df_from_text)
    df_from_text = fill_empty_elements(df_from_text)
    return df_from_text

def full_print(df):
    from rich import print as rprint
    for i in range(len(df)):
        print(f"--- Chunk: {i} Level: {df.loc[i, 'H_level']} -- {df.loc[i, 'num_tokens']} tokens -- Parent:{df.loc[i, 'H1_parent']} ---")
        rprint(df.loc[i, 'text'])

def pretty_print(df):
    from rich import print as rprint
    for i in range(len(df)):
        print(f"--####-- Chunk: {i} -####--")
        rprint(df.loc[i, 'text'])
