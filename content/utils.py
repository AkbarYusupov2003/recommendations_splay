def wrong_cyrillic_translate(s1):
    translation = dict()

    translation[ord("`")] = "ё"

    translation[ord("q")] = "й"
    translation[ord("w")] = "ц"
    translation[ord("e")] = "у"
    translation[ord("r")] = "к"
    translation[ord("t")] = "е"
    translation[ord("y")] = "н"
    translation[ord("u")] = "г"
    translation[ord("i")] = "ш"
    translation[ord("o")] = "щ"
    translation[ord("p")] = "з"
    translation[ord("[")] = "х"
    translation[ord("]")] = "ъ"

    translation[ord("a")] = "ф"
    translation[ord("s")] = "ы"
    translation[ord("d")] = "в"
    translation[ord("f")] = "а"
    translation[ord("g")] = "п"
    translation[ord("h")] = "р"
    translation[ord("j")] = "о"
    translation[ord("k")] = "л"
    translation[ord("l")] = "д"
    translation[ord(";")] = "ж"
    translation[ord("'")] = "э"

    translation[ord("z")] = "я"
    translation[ord("x")] = "ч"
    translation[ord("c")] = "с"
    translation[ord("v")] = "м"
    translation[ord("b")] = "и"
    translation[ord("n")] = "т"
    translation[ord("m")] = "ь"
    translation[ord(",")] = "б"
    translation[ord(".")] = "ю"
    translation[ord("/")] = "."

    return s1.translate(translation)


def to_cyrillic_translate(s1):
    translation = dict()
    translation[ord("c")] = "к"
    translation[ord("a")] = "а"
    translation[ord("b")] = "б"
    translation[ord("d")] = "д"
    translation[ord("e")] = "е"
    translation[ord("f")] = "ф"
    translation[ord("g")] = "г"

    translation[ord("h")] = "х"
    translation[ord("i")] = "и"
    translation[ord("j")] = "ж"
    translation[ord("k")] = "к"
    translation[ord("l")] = "л"
    translation[ord("m")] = "м"

    translation[ord("n")] = "н"
    translation[ord("o")] = "о"
    translation[ord("p")] = "п"
    translation[ord("q")] = "к"
    translation[ord("r")] = "р"
    translation[ord("s")] = "с"

    translation[ord("t")] = "т"
    translation[ord("u")] = "у"
    translation[ord("v")] = "в"
    translation[ord("x")] = "х"
    translation[ord("y")] = "й"
    translation[ord("z")] = "з"

    s1 = s1.replace("sh", "ш").replace("ya", "я").replace("ch", "ч")

    return s1.translate(translation)


def remove_quotes(s1):
    translation_table = str.maketrans("", "", "‘’'`")
    return s1.translate(translation_table)


# -----------------------------------------------------------------------
import requests


kinopoisk_token = "DG0DEXV-EDW43B2-G3N8J6K-BA8ECZ6"
headers = {"X-API-KEY": kinopoisk_token}


def kinopoisk_by_id():
    url = "https://api.kinopoisk.dev/v1.4/movie/1" # 5304403

    response = requests.get(headers=headers, url=url)
    result = response.json()

    persons = result["persons"]

    # for person in persons:

    print("result: ", result["persons"])


def kinopoisk_filter():
    url = "https://api.kinopoisk.dev/v1.4/movie?year=2023&genres.name=криминал"

    response = requests.get(headers=headers, url=url)
    result = response.json()["docs"]
    print("result: ", result[0]) # .get("description")


def kinopoisk_by_slug():
    url = "https://api.kinopoisk.dev/v1.4/list?page=1&limit=10&slug=honourable_mentions_XXI"

    response = requests.get(headers=headers, url=url)
    result = response.json()
    print("result: ", result)
