def four_digit_number(
        number: int,
):
    number_length = len(str(number))
    if number_length <= 4:
        return number
    elif number_length < 6:
        number = str(round(number / 1000, 6 - number_length)) + "k"
    else:
        number = str(round(number / 1000)) + "k"
    return number
