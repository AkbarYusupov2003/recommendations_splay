def remove_quotes(s1):
    translation_table = str.maketrans("", "", "‘’'`")
    return s1.translate(translation_table)
