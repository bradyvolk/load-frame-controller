def unitConverter(value):
        """
        Converts unit as a str with SI units into a a float

        Return: value as float

        Precondition: value > 1 in base unit (i.e. no mHz)

        Parameters:
                value : str : frequency to be converted
        """
        assert type(value) == str

        try:
                return float(value)
        except:
                multiplier = 1
                unitPrefixes = {
                                'p':10**-12, 'n':10**-9,
                                'micro':10**-6, 'm':10**-3,
                                'c':10**-2, 'd':10**-1,
                                'da':10**1, 'h':10**2,
                                'k':10**3, 'M':10**6,
                                'G':10**9, 'T':10**12
                                }

                for pref in unitPrefixes:
                        if pref in value:
                                if pref == 'd' and 'da' not in value:
                                        multiplier = unitPrefixes[pref]
                                        break
                                elif pref == 'h' and 'z' not in value:          # Not to get mixed with Hz
                                        multiplier = unitPrefixes[pref]
                                elif pref != 'd' and pref != 'h':
                                        multiplier = unitPrefixes[pref]
                                        break
                pos = 0
                while value[pos].isnumeric():
                        pos+=1
                convertedValue = float(value[:pos])*multiplier
                return convertedValue

while True:
        print("hey")
        test = str(input("What do you want to convert? "))
        if test == "Nothing":
                break
        else:
                print(unitConverter(test))

