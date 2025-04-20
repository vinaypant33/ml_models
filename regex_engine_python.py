



def unit_match(expr , string):
    return expr[0] == string[0]




def match_expr(expr , string , match_length = 0):
    if len(string) == 0:
        return [True , match_length]

    if unit_match(expr , string):
        return match_expr(expr[1:] , string[1:])
    else:
        return [False  , None]


def main():
    expr = 'abz'
    string = "abc"
    [Matched  , match_length] = match_expr(expr , string)
    if Matched:
        print(f'The Matched expression is  {expr} and the string from it is matched is  {string}')
    else:
        print("The expression is not matched")



if __name__ == '__main__':
    main()

